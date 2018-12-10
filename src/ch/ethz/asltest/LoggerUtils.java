package ch.ethz.asltest;

import java.util.LinkedList;
import java.util.concurrent.atomic.AtomicLong;
import java.util.logging.ConsoleHandler;
import java.util.logging.Logger;
import java.util.logging.FileHandler;

public class LoggerUtils {

    // Define the logger
    private Logger LOGGER;
    private long lastFlushed = System.currentTimeMillis();
    private final long logginThreshold = 4 * 1000 + 500; // Threshold to log in milli-seconds

    public LinkedList<String> allMultigetRequests = new LinkedList<>();

    public LoggerUtils(Long threadID) {
        ConsoleHandler handlerObj = new ConsoleHandler();

        LOGGER = Logger.getLogger("Logger" + Long.toString(threadID));

        LOGGER.addHandler(handlerObj);

        LOGGER.removeHandler(handlerObj);

        // Make this dependent on the thread that this is running on.

        try {
           LOGGER.addHandler(new FileHandler("/home/azureuser/logs/log" + Long.toString(threadID) + ".txt"));
        } catch (Exception e) {
            System.out.println("Failed miserably!");
            e.printStackTrace();
        }
        LOGGER.setUseParentHandlers(false);

        this.resetAccumulators();

    }

    // Define the logger buffers! (which will later be written to every 30 seconds
    private long totalNum;
    private long totalGETNum;
    private long accTimeRealOffset;
    private long accTimeBetweenCreatedAndEnqueued;
    private long accTimeBetweenEnqueuedAndDequeued;
    private long accTimeBetweenDequeuedAndSentToServer;
    private long accTimeBetweenSentToServerAndReceivedResponseFromServer;
    private long accTimeBetweenReceivedResponseFromServerAndTimeSentToClient;
    private long accTimeRealDoneOffset;

    public void resetAccumulators() {
        this.totalNum = 1;
        this.totalGETNum = 1;

        this.accTimeRealOffset = 0;
        this.accTimeBetweenCreatedAndEnqueued = 0;
        this.accTimeBetweenEnqueuedAndDequeued = 0;
        this.accTimeBetweenDequeuedAndSentToServer = 0;
        this.accTimeBetweenSentToServerAndReceivedResponseFromServer = 0;
        this.accTimeBetweenReceivedResponseFromServerAndTimeSentToClient = 0;
        this.accTimeRealDoneOffset = 0;
    }

    public void addItem(
            long timeRealOffset,
            long timeBetweenCreatedAndEnqueued,
            long timeBetweenEnqueuedAndDequeued,
            long timeBetweenDequeuedAndSentToServer,
            long timeBetweenSentToServerAndReceivedResponseFromServer,
            long timeBetweenReceivedResponseFromServerAndTimeSentToClient,
            long timeRealDoneOffset,
            RequestType requestType
    ) {

        this.totalNum += 1;
        this.totalGETNum += 1;

        this.accTimeRealOffset += timeRealOffset;
        this.accTimeBetweenCreatedAndEnqueued += timeBetweenCreatedAndEnqueued;
        this.accTimeBetweenEnqueuedAndDequeued += timeBetweenEnqueuedAndDequeued;
        this.accTimeBetweenDequeuedAndSentToServer += timeBetweenDequeuedAndSentToServer;
        this.accTimeBetweenSentToServerAndReceivedResponseFromServer += timeBetweenSentToServerAndReceivedResponseFromServer;
        this.accTimeBetweenReceivedResponseFromServerAndTimeSentToClient += timeBetweenReceivedResponseFromServerAndTimeSentToClient;
        this.accTimeRealDoneOffset += timeRealDoneOffset;

        // if it's a multi-get, append to all the possible multi-gets
        if (requestType == RequestType.GET) {

            // I modified this line only for multiget requests and experiment 5
            // (because else we don't have multi-gets,
            // and this would be equivalent to also just implementing
            // a "is-multikey" flag!)

            // Create the message which will be written to file
            String message = "-|-| " +
                    Long.toString(timeRealOffset) + ", " +
                    Long.toString(timeBetweenCreatedAndEnqueued) + ", " +
                    Long.toString(timeBetweenEnqueuedAndDequeued) + ", " +
                    Long.toString(timeBetweenDequeuedAndSentToServer) + ", " +
                    Long.toString(timeBetweenSentToServerAndReceivedResponseFromServer) + ", " +
                    Long.toString(timeBetweenReceivedResponseFromServerAndTimeSentToClient) + ", " +
                    Long.toString(timeRealDoneOffset) + ", " +
                    Long.toString(this.totalGETNum) + ", " +
                    "multi-get";

            this.allMultigetRequests.add(
                    message
            );

        }


    }

    public void possibleFlush() {

        if ((System.currentTimeMillis() - lastFlushed) > logginThreshold) {

            // System.out.println("Flushing to file");

            this.flushToFile("stuff");

        }

    }

    public void flushToFile(String filename) {

        double throughput = ((double) this.totalNum / (System.currentTimeMillis() - this.lastFlushed) );

        String message = "|| " +
                Long.toString(this.accTimeRealOffset / this.totalNum) + ", " +
                Long.toString(this.accTimeBetweenCreatedAndEnqueued / this.totalNum) + ", " +
                Long.toString(this.accTimeBetweenEnqueuedAndDequeued / this.totalNum) + ", " +
                Long.toString(this.accTimeBetweenDequeuedAndSentToServer / this.totalNum) + ", " +
                Long.toString(this.accTimeBetweenSentToServerAndReceivedResponseFromServer / this.totalNum) + ", " +
                Long.toString(this.accTimeBetweenReceivedResponseFromServerAndTimeSentToClient / this.totalNum) + ", " +
                Long.toString(this.accTimeRealDoneOffset / this.totalNum) + ", " +
                Long.toString(this.totalNum) + ", " +
                Double.toString(throughput);

        // System.out.println(message);
        LOGGER.severe(message);

        if (allMultigetRequests.size() > 0) {

            for (String multikeyMessage : this.allMultigetRequests) {
                LOGGER.severe(multikeyMessage);
            }

            this.allMultigetRequests.clear();

        }

        this.resetAccumulators();
        this.lastFlushed = System.currentTimeMillis();

    }


}
