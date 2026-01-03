package utils;

public class Protocol {
    //client commands
    public static final String LOGIN = "LOGIN";
    public static final String UPLOAD = "UPLOAD";
    public static final String DOWNLOAD = "DOWNLOAD";
    public static final String LIST_CLIENTS = "LIST_CLIENTS";
    public static final String LIST_OWN_FILES = "LIST_OWN_FILES";
    public static final String LIST_PUBLIC_FILES = "LIST_PUBLIC_FILES";
    public static final String UPLOAD_REQUEST = "UPLOAD_REQUEST";
    public static final String UPLOAD_CHUNK = "UPLOAD_CHUNK";
    public static final String UPLOAD_COMPLETE = "UPLOAD_COMPLETE";
    public static final String DOWNLOAD_REQUEST = "DOWNLOAD_REQUEST";
    public static final String MAKE_FILE_REQUEST = "MAKE_FILE_REQUEST";
    public static final String VIEW_MESSAGES = "VIEW_MESSAGES";
    public static final String VIEW_HISTORY = "VIEW_HISTORY";
    public static final String LOGOUT = "LOGOUT";


    public static final String PUBLIC = "PUBLIC";
    public static final String PRIVATE = "PRIVATE";

    public static final String BUFFER_FULL = "BUFFER_FULL";
    public static final String UPLOAD_CONFIRMED = "UPLOAD_CONFIRMED";
    public static final String DOWNLOAD_COMPLETE = "DOWNLOAD_COMPLETE";
    public static final String DOWNLOAD_START = "DOWNLOAD_START";
    public static final String CHUNK_ACK = "CHUNK_ACK";



    //server responses
    public static final String DENIED = "DENIED";
    public static final String DELIMITER = ":::";
    public static final String SUCCESS = "SUCCESS";
    public static final String ERROR = "ERROR";
}
