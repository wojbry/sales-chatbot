// src/components/ChatAgent.js
import React, { useState, useEffect, useRef } from 'react';

// IMPORTANT: Replace with your actual Agent Engine (Cloud Run) API Endpoint
const AGENT_API_ENDPOINT = "put endpoint here";

const ChatAgent = () => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!inputMessage.trim() || isLoading) return;

        const userMessage = { sender: 'user', text: inputMessage };
        setMessages((prev) => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);

        // Check if the API endpoint is set
        if (AGENT_API_ENDPOINT === "YOUR_AGENT_API_ENDPOINT") {
            setMessages((prev) => [
                ...prev,
                { sender: 'agent', text: "ERROR: Agent API Endpoint is not set. Please replace 'YOUR_AGENT_API_ENDPOINT' in src/components/ChatAgent.js." }
            ]);
            setIsLoading(false);
            return;
        }

        try {
            const response = await fetch(AGENT_API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: inputMessage }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            // Assuming your agent returns a JSON with an "answer" field
            setMessages((prev) => [...prev, { sender: 'agent', text: data.answer || "No specific answer received, check agent logs." }]);
        } catch (error) {
            console.error("Error communicating with agent:", error);
            setMessages((prev) => [...prev, { sender: 'agent', text: `Sorry, there was an error: ${error.message}. Please check console for details.` }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="chat-agent-container">
            <h2>Ask Your Data Agent</h2>
            <div className="messages-display">
                {messages.length === 0 ? (
                    <p className="no-messages-tip">Type a question to start, e.g., "What were the total sales for Basic T-Shirt last month?"</p>
                ) : (
                    messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.sender}`}>
                            {msg.sender === 'user' && <strong>You: </strong>}
                            {msg.sender === 'agent' && <strong>Agent: </strong>}
                            {msg.text}
                        </div>
                    ))
                )}
                {isLoading && (
                    <div className="message agent loading">
                        <strong>Agent: </strong>Typing...
                    </div>
                )}
                <div ref={messagesEndRef} /> {/* For auto-scrolling */}
            </div>
            <form onSubmit={handleSendMessage} className="message-input-form">
                <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Type your question here..."
                    disabled={isLoading}
                />
                <button type="submit" disabled={isLoading}>
                    Send
                </button>
            </form>
        </div>
    );
};

export default ChatAgent;