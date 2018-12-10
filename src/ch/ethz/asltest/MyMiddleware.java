package ch.ethz.asltest;

import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.nio.charset.Charset;
import java.util.*;

// Trying to understand this stupid thing on
// https://examples.javacodegeeks.com/core-java/nio/java-nio-socket-example/

// Following the nio tutorial here
// https://www.baeldung.com/java-nio-selector

import java.net.InetSocketAddress;
import java.io.*;

// Server specific imports


// Pool specific imports
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.Semaphore;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

public class MyMiddleware {

    // ARGUMENTS TO FUNCTION SAVED JUST IN CASE
    private String currentIp;
    private int listeningPort;
    private List<String> memcachedAdresses;
    private int numberOfThreads; // Why is this not recognized?
    private boolean readSharded;

    private LinkedList<Semaphore> inputLockList = new LinkedList<>();
    private LinkedList<Semaphore> outputLockList = new LinkedList<>();

    private ThreadPoolExecutor threadPool;

    // Have one single thread listening for new requests.
    // Create these new requests, put them in a queue
    // Let each request spawn a new thread to act upon, and answer with one of the servers
    Selector incomingServerRequestSelector;
    ServerSocketChannel serverSocketChannel;

    public MyMiddleware(
            String currentIP,
            int listeningPort,
            List<String> memcachedAdresses,
            int numberOfThreads,
            boolean readSharded
    ) {

        // Start with naively redirecting the input to the output port
        this.currentIp = currentIP;
        this.listeningPort = listeningPort;
        this.memcachedAdresses = memcachedAdresses;
        this.numberOfThreads = numberOfThreads;
        this.readSharded = readSharded;

        // Setup the memtier port list

        // Setup the memcached port list

        // Listen to the input port!
        // Listening to input :: http://tutorials.jenkov.com/java-nio/server-socket-channel.html
        try {
            serverSocketChannel = ServerSocketChannel.open();
            serverSocketChannel.socket().bind(
                    new InetSocketAddress(this.currentIp, this.listeningPort),
                    2 * 32 * 2 * 3
            );
            // Make it non-blocking
            serverSocketChannel.configureBlocking(false);

        } catch (IOException e) {
            e.printStackTrace();
            System.out.println("FAILING :: MyMiddleware :: 1");
        }

        // Create a selector which we will use to configure between multiple incoming requests
        // and register the serverSocketChannel to the Selector
        try {
            this.incomingServerRequestSelector = Selector.open();
            assert this.serverSocketChannel != null;
            this.serverSocketChannel.register(
                    this.incomingServerRequestSelector,
                    SelectionKey.OP_ACCEPT
            );
        } catch (IOException e) {
            e.printStackTrace();
            System.out.println("FAILING :: MyMiddleware :: 2");
        }

//        System.out.println("Got this far");

    }

    /**
     * Given a request from a memtier instance, checks if that request is complete
     *
     * @param byteBuffer
     * @return
     */
    private boolean requestIsComplete(ByteBuffer byteBuffer) throws java.lang.StringIndexOutOfBoundsException {

        int latestIndex = 0;
        int number_of_newlines = 0;

        String request = new String(byteBuffer.array(), 0, byteBuffer.limit());

        char firstCharacter = request.charAt(0);


        while(true){
            latestIndex = request.indexOf("\r\n", latestIndex);

            if(latestIndex >= 0){
                number_of_newlines += 1;
                latestIndex += 2;
            }

            if (latestIndex < 0){
                break;
            }

        }

        switch (firstCharacter) {
            case 's':
                return number_of_newlines == 2;
            case 'g':
                return number_of_newlines == 1;
            default:
                System.out.println("Something went wrong!!!");
                System.out.println(firstCharacter);
                return false;
        }

    }

    /**
     * Runs the main logic
     */
    public void run() {

        // Setting up the queue that this process will write to
        LinkedBlockingQueue<Runnable> workQueue = new LinkedBlockingQueue<Runnable>();
        // Setting up the workers that will operate on this queue

        this.threadPool = new ThreadPoolExecutor(
                this.numberOfThreads,
                this.numberOfThreads,
                0,
                TimeUnit.SECONDS,
                workQueue
        );

        // Read requests
        try {

            boolean firstTryDone = false;
            boolean isComplete;

            while (!firstTryDone || this.incomingServerRequestSelector.keys().size() != 1) {


                this.incomingServerRequestSelector.select(2000);

                ByteBuffer byteBuffer;
                SocketChannel socketChannel;
                int numberOfBytesRead;
                SingleRequest singleRequest;

//                System.out.println("Still kill");

                for (SelectionKey key : this.incomingServerRequestSelector.selectedKeys()) {

//                    System.out.println("New request!");

                    // Get next byte bucket and create a new listener socket
                    if (key.isAcceptable()) {
                        firstTryDone = true;

                        // Create a new socket
                        ServerSocketChannel serverSocketChannel = (ServerSocketChannel) key.channel();
                        socketChannel = serverSocketChannel.accept();
                        socketChannel.configureBlocking(false);
                        socketChannel.register(this.incomingServerRequestSelector, SelectionKey.OP_READ);
                    }

                    // Check if the key is readable and break up else
//                    System.out.println("Checkpotin 6");
                    if (!key.isReadable()) {
                        continue;
                    }
//                    System.out.println("Checkpotin 7");

                    // Create a byte buffer
                    if (key.attachment() != null) {
//                        System.out.println("Checkpotin 7.1");
                        byteBuffer = (ByteBuffer) key.attachment();
                    } else {
//                        System.out.println("Checkpotin 7.2");
                        byteBuffer = ByteBuffer.allocate(20 * 4 * 1024); // Is this buffer big enough?
                    }

                    socketChannel = (SocketChannel) key.channel();
//                    System.out.println("Checkpotin 8");

                    assert byteBuffer.position() == 0;

                    numberOfBytesRead = socketChannel.read(byteBuffer);

//                    System.out.println("Request is: ");
//                    System.out.println(numberOfBytesRead);

//                    System.out.println("Checkpotin 8.2");

                    // Check if the byteBuffer is empty. If it is empty, just cancel the connection!
                    if (numberOfBytesRead < 0) {
//                        System.out.println("Request canceled!");
                        key.cancel();
                        continue;
                    }

//                    System.out.println("Request  notcanceled!");

                    // Append to bytebuffer, or create request
                    try {
                        isComplete = this.requestIsComplete(byteBuffer);
                    } catch (Exception e) {
                        System.out.println("ERROR: Checking if request is complete failed!");
                        e.printStackTrace();
                        break;
                    }

                    if (!isComplete) {
                        key.attach(byteBuffer);
                    } else {

//                        System.out.println("Queuing...");

                        // Do whatever you have to do with the channel;
                        singleRequest = new SingleRequest(byteBuffer, socketChannel, this.readSharded);

                        MiddlewareWorker worker = new MiddlewareWorker(
                                readSharded,
                                singleRequest,
                                this.memcachedAdresses
                        );
                        singleRequest.setTimeEnqueued();

                        threadPool.submit(worker);

                        key.attach(null);

                    }

                }

                this.incomingServerRequestSelector.selectedKeys().clear();

            }

            // Flush everything to one file!"

            this.threadPool.shutdown();
            this.flushAllLoggersToCSV();

        } catch (IOException e) {
            e.printStackTrace();
            System.out.println("FAILURE :: MyMiddleware :: 4");
        } catch (Exception e) {
            e.printStackTrace();
            System.out.println("FAILURE :: MyMiddleware :: 5");
        }

    }

    private void flushAllLoggersToCSV() {

        Iterator it = MiddlewareWorker.threadID2Logger.entrySet().iterator();
        while (it.hasNext()) {

            Map.Entry pair = (Map.Entry) it.next();
            LoggerUtils loggerUtilsObj = (LoggerUtils) pair.getValue();

            loggerUtilsObj.possibleFlush();

            it.remove(); // avoids a ConcurrentModificationException
        }

    }

}