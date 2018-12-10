package ch.ethz.asltest;

import java.util.*;

public class RunMW {

    static String myIp = null;
    static int myPort = 0;
    static List<String> mcAddresses = null;
    static int numThreadsPTP = -1;
    static boolean readSharded = false;

    public static void main(String[] args) throws Exception {

        // -----------------------------------------------------------------------------
        // Parse and prepare arguments
        // -----------------------------------------------------------------------------

        parseArguments(args);

        // -----------------------------------------------------------------------------
        // Start the Middleware
        // -----------------------------------------------------------------------------

        new MyMiddleware(myIp, myPort, mcAddresses, numThreadsPTP, readSharded).run();

    }

    private static void parseArguments(String[] args) {
        Map<String, List<String>> params = new HashMap<>();

        List<String> options = null;
        for (int i = 0; i < args.length; i++) {
            final String a = args[i];

            if (a.charAt(0) == '-') {
                if (a.length() < 2) {
                    System.err.println("Error at argument " + a);
                    System.exit(1);
                }

                options = new ArrayList<String>();
                params.put(a.substring(1), options);
            } else if (options != null) {
                options.add(a);
            } else {
                System.err.println("Illegal parameter usage");
                System.exit(1);
            }
        }

        if (params.size() == 0) {
            printUsageWithError(null);
            System.exit(1);
        }

        if (params.get("l") != null)
            myIp = params.get("l").get(0);
        else {
            printUsageWithError("Provide this machine's external IP! (see ifconfig or your VM setup)");
            System.exit(1);
        }

        if (params.get("p") != null)
            myPort = Integer.parseInt(params.get("p").get(0));
        else {
            printUsageWithError("Provide the port, that the middleware listens to (e.g. 11212)!");
            System.exit(1);
        }

        if (params.get("m") != null) {
            mcAddresses = params.get("m");
        } else {
            printUsageWithError(
                    "Give at least one memcached backend server IP address and port (e.g. 123.11.11.10:11211)!");
            System.exit(1);
        }

        if (params.get("t") != null)
            numThreadsPTP = Integer.parseInt(params.get("t").get(0));
        else {
            printUsageWithError("Provide the number of threads for the threadpool!");
            System.exit(1);
        }

        if (params.get("s") != null)
            readSharded = Boolean.parseBoolean(params.get("s").get(0));
        else {
            printUsageWithError("Provide true/false to enable sharded reads!");
            System.exit(1);
        }

    }

    private static void printUsageWithError(String errorMessage) {
        System.err.println();
        System.err.println(
                "Usage: -l <MyIP> -p <MyListenPort> -t <NumberOfThreadsInPool> -s <readSharded> -m <MemcachedIP:Port> <MemcachedIP2:Port2> ...");
        if (errorMessage != null) {
            System.err.println();
            System.err.println("Error message: " + errorMessage);
        }

    }
}