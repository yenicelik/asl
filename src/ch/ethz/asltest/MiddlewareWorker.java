package ch.ethz.asltest;

import java.io.*;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;
import java.nio.charset.Charset;
import java.util.Arrays;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;

/**
 * Skip logging for now
 */


public class MiddlewareWorker implements Runnable {

    // Have one selector select between multiple channels (single thread selecting amongst multiple threads)
    private boolean readSharded;
    Integer numberOfBucket;
    private SingleRequest singleRequest;
    private List<String> memcachedAdresses;

    private static HashMap<Long, List<SocketChannel>> threadID2Server = new HashMap<>();
    public static HashMap<Long, LoggerUtils> threadID2Logger = new HashMap<>();

    // Have ports for each possible client
    // Have servers for each possible server

    public MiddlewareWorker(
            boolean readSharded,
            SingleRequest singleRequest,
            List<String> memcachedAdresses
    ) {

        this.readSharded = readSharded;
        this.numberOfBucket = memcachedAdresses.size();
        this.singleRequest = singleRequest;
        this.memcachedAdresses = memcachedAdresses;

    }

    /**
     * For each individual worker, we set up a a new list of socket workers
     *
     * @return
     */
    private LinkedList<SocketChannel> generateSocketChannelsForSingleWorker() throws IOException {

        // Preparing what we're gonna output
        LinkedList<SocketChannel> individiualSocketChannels = new LinkedList<SocketChannel>();

        // Stuff that needs to be set
        assert this.memcachedAdresses != null;
        assert this.memcachedAdresses.size() > 0;

        // Spawn each worker thread, and let it connect to the respective port
        for (String memcachedAddress : this.memcachedAdresses) {
            String[] ip_and_port = memcachedAddress.split(":");
            assert ip_and_port.length == 2;
            String memcachedAddressIP = ip_and_port[0];
            Integer memcachedAddressPort = Integer.parseInt(ip_and_port[1]);

            SocketChannel socketChannel = SocketChannel.open();
            socketChannel.connect(
                    new InetSocketAddress(memcachedAddressIP, memcachedAddressPort)
            );
            // Set the listener to blocking, because we need to send back the result before acting on a new one
            socketChannel.configureBlocking(true);

            // Add the socket to the list
            individiualSocketChannels.add(socketChannel);

        }

        assert individiualSocketChannels.size() > 0;
        assert individiualSocketChannels.size() == this.memcachedAdresses.size();

        return individiualSocketChannels;

    }

    private LoggerUtils getLogger() {
        Long threadID = Thread.currentThread().getId();

        LoggerUtils logger = this.threadID2Logger.get(threadID);

        if (logger == null) {
            // Create new socket
            logger = new LoggerUtils(threadID);
            threadID2Logger.put(threadID, logger);
        }

        return logger;
    }

    private SocketChannel getSocketChannel(int bucketID) throws IOException {

        Long threadID = Thread.currentThread().getId();

        // Get the list from the hashmap
        List<SocketChannel> listOfSocketChannel = threadID2Server.get(threadID);
        if (listOfSocketChannel == null) {
            // Create new socket
            listOfSocketChannel = this.generateSocketChannelsForSingleWorker();
            threadID2Server.put(threadID, listOfSocketChannel);
        }

        SocketChannel out = listOfSocketChannel.get(bucketID);

        return out;

    }

    private boolean responseIsComplete(ByteBuffer byteBuffer) {
        String request = new String(byteBuffer.array(), 0, byteBuffer.position());
        // TODO This changed (previously uncommented!
//        if (request.length() > 5) {
//            return false;
//        }
        return request.endsWith("END\r\n");
    }

    private ByteBuffer sendSingleShardRequest(ByteBuffer byteBuffer, SocketChannel socketChannel) throws IOException {

        // Create a new byteBuffer to read in the response into

        byteBuffer = ByteBuffer.allocate(15 * 4 * 1024);

        boolean isComplete;
        while (!(isComplete = responseIsComplete(byteBuffer))) {
            socketChannel.read(byteBuffer);
        }

        byteBuffer.flip(); // reset buffer pointer to beginning

        return byteBuffer;
    }

    private ByteBuffer doTheSharding(String[] allKeys, Integer start, Integer end, boolean appendCarriage) {
        String getCommand = "get ";
        String[] subArray = (String[]) Arrays.copyOfRange(allKeys, start, end);
        String sendValue = getCommand + String.join(" ", subArray);
        if (appendCarriage) {
            sendValue += "\r\n";
        }

        ByteBuffer byteBuffer = this.stringToByteBuffer(sendValue);

        return byteBuffer;
    }

    /**
     * Send the single request to a single server (decided by the hash)
     *
     * @param singleRequest
     * @return
     */
    public void handleNonshardedGetRequest(SingleRequest singleRequest) throws IOException {
//        String rrr; // For debug purposes

//        System.out.println("non sharded get!");

        Integer bucketID = singleRequest.requestString.hashCode() % this.numberOfBucket;
        bucketID = Math.abs(bucketID);


        SocketChannel socketChannel = this.getSocketChannel(bucketID);

        // Get the byte buffer from the single request
        ByteBuffer byteBuffer = singleRequest.byteBuffer;

//        System.out.println("Writing to server!!");
//        String rrr = new String(Arrays.copyOfRange(byteBuffer.array(), 0, byteBuffer.limit()));
//        System.out.println(rrr);

        socketChannel.write(byteBuffer);

        // Written to all servers
        // Record when exactly the SingleRequest is created TODO LOGGER
        this.singleRequest.setTimeSentToServer();


        byteBuffer = this.sendSingleShardRequest(byteBuffer, socketChannel);

//        System.out.println("Getting from server!!");
//        rrr = new String(Arrays.copyOfRange(byteBuffer.array(), 0, byteBuffer.limit()));
//        System.out.println(rrr);

        // Written to all servers
        // Record when exactly the SingleRequest is created TODO LOGGER
        this.singleRequest.setTimeReceivedResponseFromServer();

//        System.out.println("Writing... back to the client!!");
//        rrr = new String(Arrays.copyOfRange(byteBuffer.array(), 0, byteBuffer.limit()));
//        System.out.println(rrr);

        try {
            singleRequest.socketChannel.write(byteBuffer); // Send back to the memtier server
        } catch (Exception e) {
            e.printStackTrace();
        }

//        System.out.println("Written back to the client!!");

        // Written to all servers
        // Record when exactly the SingleRequest is created TODO LOGGER
        this.singleRequest.setTimeSentToClient();
        this.singleRequest.writeToLogger(this.getLogger());

    }

    /**
     * Split up the request into multiple get keys and send the keys individually to different servers (decided by the hash)
     *
     * @param singleRequest
     * @return
     */
    private void handleShardedGetRequest(SingleRequest singleRequest) throws IOException {

        String request = singleRequest.requestString;
        String[] all_keys = request.split(" ");
        String[] getKeys = Arrays.copyOfRange(all_keys, 1, all_keys.length);

        String responseAnswers = "";
        StringBuilder responseAnswer = new StringBuilder();

        // Do the stupid math
        int total_servers = getKeys.length / this.numberOfBucket;
        int leftout_keys = getKeys.length % this.numberOfBucket;

        int total = 0;

        // Written to all servers
        // Record when exactly the SingleRequest is created TODO LOGGER
        this.singleRequest.setTimeSentToServer(); // TODO: This is somehow wrong!

        for (Integer bucketID = 0; bucketID < this.numberOfBucket; bucketID++) {

            SocketChannel socketChannel = this.getSocketChannel(bucketID);

            // Calculate which server to put it into
            int numKeysToPutIntoBucket = total_servers;
            if (bucketID < leftout_keys) {
                numKeysToPutIntoBucket += 1;
            } else if (total_servers == 0) {
                numKeysToPutIntoBucket += 1;
            }

            boolean carriageReturn = true;
            if (bucketID == this.numberOfBucket - 1) {
                carriageReturn = false;
            } else if ((total_servers == 0) && (bucketID == leftout_keys - 1)) {
                carriageReturn = false;
            }

            // TODO: This indexing could be the source of many bugs! Watch this
            // Break out of loop if we have the index is done
            if ((total_servers == 0) && (total >= leftout_keys)) {
                break;
            }

            ByteBuffer byteBuffer = this.doTheSharding(getKeys, total, total + numKeysToPutIntoBucket, carriageReturn);

            // Save all the request in a bytebuffer (and take out the \r\n each time)
            socketChannel.write(byteBuffer);

            byteBuffer = this.sendSingleShardRequest(byteBuffer, socketChannel);

            request = request.split("END")[0];

            // Append to string
            responseAnswer.append(request + "\r\n");

            byteBuffer.clear();

            total += numKeysToPutIntoBucket;

        }

        // Written to all servers
        // Record when exactly the SingleRequest is created TODO LOGGER
        this.singleRequest.setTimeReceivedResponseFromServer(); // TODO: This is somehow wrong!

        String jointResponse = responseAnswers.toString();
        // Remove the very last \r\n
        jointResponse += "END\r\n";

        // Send the joint request
        ByteBuffer clientResponseByteBuffer = this.stringToByteBuffer(jointResponse);

        singleRequest.socketChannel.write(clientResponseByteBuffer); // Send back to the memtier server

        // Written to all servers
        // Record when exactly the SingleRequest is created TODO LOGGER
        this.singleRequest.setTimeSentToClient(); // TODO: This is somehow wrong!
        this.singleRequest.writeToLogger(this.getLogger());

    }

    private ByteBuffer stringToByteBuffer(String inputValue) {
        ByteBuffer buffer = Charset.forName("UTF-8").encode(inputValue);
        return buffer;
    }

    private boolean checkIfSETwasStored(ByteBuffer byteBuffer) {
        String response = new String(Arrays.copyOfRange(byteBuffer.array(), 0, byteBuffer.position()));
        boolean firstFlag = response.endsWith("STORED\r\n");
        if (firstFlag) {
            boolean secondFlag = response.endsWith("NOT STORED\r\n");
            return !secondFlag;
        }
        return false;
    }

    /**
     * Send the single request as a setter to ALL the servers.
     * If there is a single error, return the error
     *
     * @param singleRequest
     * @return
     */
    public void handleSetRequest(SingleRequest singleRequest) throws IOException {

        ByteBuffer byteBuffer = null;
        boolean successfulStore = true;

        for (int bucketID = 0; bucketID < this.numberOfBucket; bucketID++) {
            // Get the byte buffer from the single request
            byteBuffer = singleRequest.byteBuffer;

//            System.out.println("SET: Writing to server!");
//            String response = new String(Arrays.copyOfRange(singleRequest.byteBuffer.array(), 0, byteBuffer.position()));
//            System.out.println(response);


            // Get the socket channel that you're going to write to
            SocketChannel socketChannel = this.getSocketChannel(bucketID);

            // Create a new byteBuffer to read in the response into
            socketChannel.write(byteBuffer);
            byteBuffer.flip(); // reset buffer pointer to beginning

        }

        // Written to all servers
        // Record when exactly the SingleRequest is created TODO LOGGER
        this.singleRequest.setTimeSentToServer();

        int isError = 0;

        // Now getting all the responses from the bus
        for (int bucketID = 0; bucketID < this.numberOfBucket; bucketID++) {

            SocketChannel socketChannel = this.getSocketChannel(bucketID);

            byteBuffer.clear();
            byteBuffer = ByteBuffer.allocate(15 * 4 * 1024);

            socketChannel.read(byteBuffer);

            // TODO: add some sort of delimiter to check when a single request is sent to multiple servers! (request id could solve this?)

            // check if the value is STORED1
            successfulStore = this.checkIfSETwasStored(byteBuffer);

            if (!successfulStore) {
                isError += 1;
            }

            if (isError == 1) {
                singleRequest.socketChannel.write(byteBuffer); // Send back to the memtier server
            }

            byteBuffer.flip(); // reset buffer pointer to beginning

        }

        // Written to all servers
        // Record when exactly the SingleRequest is created TODO LOGGER
        this.singleRequest.setTimeReceivedResponseFromServer(); // TODO: This is somehow wrong!


        if (isError == 0) {
            singleRequest.socketChannel.write(byteBuffer);
        }

        // Written to all servers
        // Record when exactly the SingleRequest is created TODO LOGGER
        this.singleRequest.setTimeSentToClient();
        this.singleRequest.writeToLogger(this.getLogger());

    }

    public void run() {

//        System.out.println("Dequeuing...");

        // Dequeing...
        // Record when exactly the SingleRequest is created TODO LOGGER

        // Set the thread id:
        this.singleRequest.setThreadId();

        this.singleRequest.setTimeDequeued();

        // Sending the request to the respective handler
        try {
            switch (this.singleRequest.requestType) {
                case GET:
                    if (this.readSharded) {
                        this.handleShardedGetRequest(this.singleRequest);
                    } else {
//                        System.out.println("GET!");
                        this.handleNonshardedGetRequest(this.singleRequest);
                    }
                    break;
                case SET:
//                    System.out.println("SET!");
                    this.handleSetRequest(this.singleRequest);
                    break;
            }
        } catch (Exception e) {
            System.out.println("Error writing and reading response from memcached!");
            e.printStackTrace();
            assert false;
        }

//        System.out.println("DONE!");


//        this.getLogger().flushToFile("stuffLoggerFilename");

    }
}
