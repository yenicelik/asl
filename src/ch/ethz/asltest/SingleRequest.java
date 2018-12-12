package ch.ethz.asltest;

import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;
import java.nio.charset.Charset;
import java.time.Duration;
import java.time.Instant;

public class SingleRequest {
    /**
     * We fill this class with ALL the information that the client or server may assign.
     * This is a global object that gets passed
     */

    // For memory purposes, we simply save the byte buffer as a variable
    public String requestString;
    public ByteBuffer byteBuffer;
    public RequestType requestType; // Can be one of
    public SocketChannel socketChannel;
    public boolean sharded;

    public long timeRealOffset;
    public Instant timeCreated;
    public Instant timeEnqueued;
    public Instant timeDequeued;
    public Instant timeSentToServer;
    public Instant timeReceivedResponseFromServer;
    public Instant timeSentToClient;
    public long timeRealDoneOffset;
    public long queueSize;

     private long threadId;

    public void setThreadId() {
        this.threadId = Thread.currentThread().getId();
    }


    // Measuring everything possilbe
    // All the operations which set the corresponding times
    public void setTimeCreated(Integer queueSize) {
        this.timeRealOffset = System.currentTimeMillis();
        this.timeCreated = Instant.now();
        this.queueSize = queueSize.longValue();
    }
    public void setTimeEnqueued() {
        this.timeEnqueued = Instant.now();
    }
    public void setTimeDequeued() {
        this.timeDequeued = Instant.now();
    }
    public void setTimeSentToServer() {

        this.timeSentToServer = Instant.now();
    }
    public void setTimeReceivedResponseFromServer() {
        this.timeReceivedResponseFromServer = Instant.now();
    }
    public void setTimeSentToClient() {
        this.timeSentToClient = Instant.now();
        this.timeRealDoneOffset = System.currentTimeMillis();

        // Create a unique id for this request?
        // uuid = UUID.randomUUID().toString();
    }

    //
    private RequestType getRequestType(String requestString) {
        char firstCharacter = requestString.charAt(0);

        switch (firstCharacter) {
            case 's':
                return RequestType.SET;
            case 'g':
                return RequestType.GET;
            default:
                System.out.println("Something went wrong!!!");
                assert false;
                return null;
        }

    }

    public SingleRequest(
            ByteBuffer byteBuffer,
            SocketChannel socketChannel,
            boolean sharded,
            Integer queueSize
    ) {

        this.byteBuffer = byteBuffer;
        this.requestString = new String(byteBuffer.array(), 0, byteBuffer.position(), Charset.forName("UTF-8"));
        this.byteBuffer.flip(); // flipped here to be read from
        this.requestType = this.getRequestType(this.requestString);
        this.socketChannel = socketChannel;
        this.sharded = sharded;

        // Record when exactly the SingleRequest is created TODO LOGGER
        this.setTimeCreated(queueSize);

    }

    /**
     * Append to a logger file the time events for this file.
     * This should maybe add to a buffer which gets flushed every now and then
     * This create a CSV - comma seperated logging item starting with a || to make parsing easier later
     */
    public void writeToLogger(LoggerUtils loggerUtils) {
        // Appending to a logger file
        // TODO

        String type = "get";

        switch (this.requestType) {
            case SET:
                type = "set";
                break;
            case GET:
                String[] keys = this.requestString.split(" ");
                if (keys.length > 2) {
                    type = "multiget";
                } else {
                    type = "get";
                }
                break;
        }

        // First difference

        // Write the logging message to the logger buffer or directly to disk
        loggerUtils.addItem(
                this.timeRealOffset,
                Duration.between(timeCreated, timeEnqueued).getNano(),
                Duration.between(timeEnqueued, timeDequeued).getNano(),
                Duration.between(timeDequeued, timeSentToServer).getNano(),
                Duration.between(timeSentToServer, timeReceivedResponseFromServer).getNano(),
                Duration.between(timeReceivedResponseFromServer, timeSentToClient).getNano(),
                timeRealDoneOffset,
                requestType,
                this.queueSize
                );

        loggerUtils.possibleFlush();

    }

}