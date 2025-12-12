package models;

import java.io.Serializable;
import java.util.Date;


//FileRequest represents a file request made by a client

public class FileRequest implements Serializable {
    private String requestID;
    private String requester;
    private String recipient; // username or "ALL"
    private String description;
    private Date timestamp;
    private boolean fulfilled;
    
    public FileRequest(String requestID, String requester, String recipient, String description) {
        this.requestID = requestID;
        this.requester = requester;
        this.recipient = recipient;
        this.description = description;
        this.timestamp = new Date();
        this.fulfilled = false;
    }
    
    public String getRequestID() { return requestID; }
    public String getRequester() { return requester; }
    public String getRecipient() { return recipient; }
    public String getDescription() { return description; }
    public Date getTimestamp() { return timestamp; }
    public boolean isFulfilled() { return fulfilled; }
    public void setFulfilled(boolean fulfilled) { this.fulfilled = fulfilled; }
}