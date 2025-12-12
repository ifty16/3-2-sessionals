package models;

import java.io.Serializable;
import java.util.Date;


//Message represents notifications sent to clients
public class Message implements Serializable {
    private String messageID;
    private String recipient;
    private String content;
    private Date timestamp;
    private boolean read;
    
    public Message(String messageID, String recipient, String content) {
        this.messageID = messageID;
        this.recipient = recipient;
        this.content = content;
        this.timestamp = new Date();
        this.read = false;
    }
    
    public String getMessageID() { return messageID; }
    public String getRecipient() { return recipient; }
    public String getContent() { return content; }
    public Date getTimestamp() { return timestamp; }
    public boolean isRead() { return read; }
    public void setRead(boolean read) { this.read = read; }
    public void setTimestamp(Date timestamp) { this.timestamp = timestamp; }
}