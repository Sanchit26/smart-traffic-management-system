import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiMessageSquare, 
  FiAlertTriangle, 
  FiInfo,
  FiSend,
  FiCpu,
  FiUser
} from 'react-icons/fi';
import { useSocket } from '../context/SocketContext';

const AlertItem = ({ alert, index }) => {
  const getAlertIcon = (type) => {
    switch (type) {
      case 'accident': return <FiAlertTriangle className="w-4 h-4 text-red-500" />;
      case 'emergency': return <FiAlertTriangle className="w-4 h-4 text-red-600" />;
      case 'congestion': return <FiInfo className="w-4 h-4 text-yellow-500" />;
      case 'maintenance': return <FiInfo className="w-4 h-4 text-blue-500" />;
      default: return <FiInfo className="w-4 h-4 text-gray-500" />;
    }
  };

  const getAlertColor = (severity) => {
    switch (severity) {
      case 'high': return 'border-red-200 bg-red-50';
      case 'medium': return 'border-yellow-200 bg-yellow-50';
      case 'low': return 'border-blue-200 bg-blue-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className={`p-4 rounded-lg border-l-4 ${getAlertColor(alert.severity)} mb-3`}
    >
      <div className="flex items-start space-x-3">
        {getAlertIcon(alert.type)}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm font-medium text-gray-800 capitalize">
              {alert.type.replace('_', ' ')}
            </span>
            <span className="text-xs text-gray-500">
              {formatTime(alert.timestamp)}
            </span>
          </div>
          <p className="text-sm text-gray-700 mb-1">{alert.message}</p>
          <p className="text-xs text-gray-500">📍 {alert.location}</p>
        </div>
      </div>
    </motion.div>
  );
};

const ChatMessage = ({ message, isBot, timestamp }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex items-start space-x-3 mb-4 ${isBot ? 'justify-start' : 'justify-end'}`}
    >
      {isBot && (
        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
          <FiCpu className="w-4 h-4 text-white" />
        </div>
      )}
      
      <div className={`max-w-xs px-4 py-2 rounded-lg ${
        isBot 
          ? 'bg-gray-100 text-gray-800' 
          : 'bg-blue-500 text-white'
      }`}>
        <p className="text-sm">{message}</p>
        <p className={`text-xs mt-1 ${
          isBot ? 'text-gray-500' : 'text-blue-100'
        }`}>
          {new Date(timestamp).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </p>
      </div>
      
      {!isBot && (
        <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
          <FiUser className="w-4 h-4 text-gray-600" />
        </div>
      )}
    </motion.div>
  );
};

const ChatbotFeed = () => {
  const { alerts } = useSocket();
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI traffic assistant. I'm monitoring all traffic signals and will alert you to any issues.",
      isBot: true,
      timestamp: new Date().toISOString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-generate AI responses to new alerts
  useEffect(() => {
    if (alerts.length > 0) {
      const latestAlert = alerts[0];
      
      // Check if we already responded to this alert
      const alreadyResponded = messages.some(msg => 
        msg.alertId === latestAlert.id && msg.isBot
      );
      
      if (!alreadyResponded) {
        setIsTyping(true);
        
        setTimeout(() => {
          const responses = {
            accident: [
              "🚨 Accident detected! I'm rerouting traffic and alerting emergency services.",
              "⚠️ Minor accident reported. Traffic flow adjusted to minimize delays.",
              "🚑 Accident at intersection. Emergency response initiated."
            ],
            emergency: [
              "🚑 Emergency vehicle detected! Clearing path and adjusting signals.",
              "🚒 Fire truck approaching. All signals cleared for priority access.",
              "🚔 Police escort in progress. Traffic diverted for safety."
            ],
            congestion: [
              "📊 High traffic density detected. Optimizing signal timing.",
              "🚗 Congestion building up. Implementing adaptive signal control.",
              "⏰ Traffic backup detected. Adjusting cycle times to improve flow."
            ],
            maintenance: [
              "🔧 Road maintenance in progress. Alternative routes suggested.",
              "🚧 Construction zone active. Reduced speed limits enforced.",
              "⚠️ Maintenance work detected. Traffic patterns adjusted."
            ]
          };
          
          const alertResponses = responses[latestAlert.type] || [
            "📋 Alert received and being processed.",
            "🔍 Analyzing traffic impact and taking necessary actions.",
            "⚡ System response initiated for the reported issue."
          ];
          
          const response = alertResponses[Math.floor(Math.random() * alertResponses.length)];
          
          setMessages(prev => [...prev, {
            id: Date.now(),
            text: response,
            isBot: true,
            timestamp: new Date().toISOString(),
            alertId: latestAlert.id
          }]);
          
          setIsTyping(false);
        }, 1500);
      }
    }
  }, [alerts, messages]);

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      const userMessage = {
        id: Date.now(),
        text: inputMessage,
        isBot: false,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, userMessage]);
      setInputMessage('');
      setIsTyping(true);
      
      // Simulate AI response
      setTimeout(() => {
        const aiResponses = [
          "I understand your concern. Let me check the current traffic conditions.",
          "Processing your request. I'll analyze the traffic patterns and provide recommendations.",
          "Thank you for the update. I'm adjusting the traffic management accordingly.",
          "I'm monitoring the situation and will take appropriate action if needed.",
          "Your input is valuable. I'm incorporating this into my traffic analysis."
        ];
        
        const response = aiResponses[Math.floor(Math.random() * aiResponses.length)];
        
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          text: response,
          isBot: true,
          timestamp: new Date().toISOString()
        }]);
        
        setIsTyping(false);
      }, 2000);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Alerts Section */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-2 mb-4">
          <FiAlertTriangle className="w-5 h-5 text-red-500" />
          <h3 className="text-lg font-semibold text-gray-800">Live Alerts</h3>
          <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
            {alerts ? alerts.length : 0}
          </span>
        </div>
        
        <div className="max-h-48 overflow-y-auto">
          <AnimatePresence>
            {alerts && alerts.length > 0 ? alerts.slice(0, 5).map((alert, index) => (
              <AlertItem key={alert.id} alert={alert} index={index} />
            )) : (
              <div className="text-center text-gray-500 py-4">
                <p>No alerts at the moment</p>
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Chat Section */}
      <div className="flex-1 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <FiMessageSquare className="w-5 h-5 text-blue-500" />
            <h3 className="text-lg font-semibold text-gray-800">AI Assistant</h3>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-xs text-gray-500">Online</span>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="space-y-4">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message.text}
                isBot={message.isBot}
                timestamp={message.timestamp}
              />
            ))}
            
            {isTyping && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-start space-x-3"
              >
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <FiCpu className="w-4 h-4 text-white" />
                </div>
                <div className="bg-gray-100 px-4 py-2 rounded-lg">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <div className="p-6 border-t border-gray-200">
          <div className="flex space-x-3">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about traffic conditions..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim()}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              <FiSend className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatbotFeed;
