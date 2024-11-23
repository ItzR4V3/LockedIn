import React, { useEffect, useState } from "react";

const Dashboard = () => {
    const [messages, setMessages] = useState([]);
    const socket = new WebSocket("ws://localhost:8000/ws/organizer");

    useEffect(() => {
        // Open WebSocket connection
        socket.onopen = () => {
            console.log("WebSocket connected");
        };

        // Receive messages
        socket.onmessage = (event) => {
            setMessages((prevMessages) => [...prevMessages, event.data]);
        };

        // Handle WebSocket errors
        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        // Close WebSocket connection
        return () => {
            socket.close();
        };
    }, []);

    const sendCommand = (studentId, command) => {
        const message = JSON.stringify({ studentId, command });
        socket.send(message); // Send command to the backend
    };

    return (
        <div>
            <h1>Organizer Dashboard</h1>
            <button onClick={() => sendCommand("student123", "LOCK_BROWSER")}>
                Lock Student Browser
            </button>
            <div>
                <h2>Messages</h2>
                {messages.map((msg, index) => (
                    <p key={index}>{msg}</p>
                ))}
            </div>
        </div>
    );
};

export default Dashboard;
