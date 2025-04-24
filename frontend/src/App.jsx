import React, { useState, useEffect, useRef, useLayoutEffect } from "react";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import jwt_decode from "jwt-decode";
import { v4 as uuidv4 } from "uuid";
import { motion, AnimatePresence } from "framer-motion";
import "./App.css";
import AIResponseBlock from "./components/AIResponseBlock";

const CLIENT_ID = "781145386370-uau90m5m63tj5rroq7roheit3hjili6t.apps.googleusercontent.com";

function App() {
  const [question, setQuestion] = useState("");
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [student, setStudent] = useState(null);
  const [history, setHistory] = useState(JSON.parse(localStorage.getItem("geometry_history")) || []);
  const [darkMode, setDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const chatContainerRef = useRef(null);
  const dropZoneRef = useRef(null);

  // Auto-scroll implementation
  useLayoutEffect(() => {
    const scrollToBottom = () => {
      if (chatContainerRef.current) {
        chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
      }
    };

    scrollToBottom();
    const timer = setTimeout(scrollToBottom, 100);
    
    return () => clearTimeout(timer);
  }, [history, loading]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (chatContainerRef.current) {
        chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
      }
    }, 0);
    
    return () => clearTimeout(timer);
  }, [darkMode]);

  useEffect(() => {
    const existing = localStorage.getItem("session_id") || uuidv4();
    localStorage.setItem("session_id", existing);
    setSessionId(existing);
  }, []);

  useEffect(() => {
    localStorage.setItem("geometry_history", JSON.stringify(history));
  }, [history]);

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('darkMode', newMode.toString());
    document.documentElement.classList.toggle('dark', newMode);
  };

  const handleAsk = async () => {
    if (!student || (!question.trim() && files.length === 0)) return;

    const formData = new FormData();
    formData.append("question", question);
    formData.append("session_id", sessionId);
    formData.append("student_name", student.name);
    formData.append("student_email", student.email);
    if (files.length > 0) formData.append("image", files[0]);

    const previews = files.map((file) => ({
      url: URL.createObjectURL(file),
      name: file.name,
    }));

    setHistory((prev) => [
      ...prev,
      {
        question: question || "",
        files: previews.length > 0 ? previews : [],
        answer: null,
      },
    ]);

    setQuestion("");
    setFiles([]);
    setLoading(true);

    try {
      const API_URL = import.meta.env.VITE_API_URL || "https://geometry-ai-tutor-backend.onrender.com/api/ask";

      const res = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });
  
      const data = await res.json();
      setHistory((prev) =>
        prev.map((entry, i) =>
          i === prev.length - 1 ? { ...entry, answer: data.response } : entry
        )
      );
    } catch (err) {
      console.error("Error:", err);
      setHistory((prev) =>
        prev.map((entry, i) =>
          i === prev.length - 1 ? { ...entry, answer: { gpt: "Sorry, something went wrong." } } : entry
        )
      );
    }

    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  const handleResetSession = () => {
    const newId = uuidv4();
    localStorage.setItem("session_id", newId);
    setSessionId(newId);
    setHistory([]);
    localStorage.removeItem("geometry_history");
    setQuestion("");
    setFiles([]);
  };

  const handleFileUpload = (incomingFiles) => {
    const newFiles = Array.from(incomingFiles).filter(
      (file) => !files.find((f) => f.name === file.name && f.size === file.size)
    );
    setFiles((prev) => [...prev, ...newFiles]);
  };

  const removeFile = (name) => {
    setFiles((prev) => prev.filter((f) => f.name !== name));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZoneRef.current?.classList.remove("ring", "ring-indigo-300");
    if (e.dataTransfer.files) handleFileUpload(e.dataTransfer.files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    dropZoneRef.current?.classList.add("ring", "ring-indigo-300");
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    dropZoneRef.current?.classList.remove("ring", "ring-indigo-300");
  };

  return (
    <GoogleOAuthProvider clientId={CLIENT_ID}>
      <div className={`min-h-screen w-full ${darkMode ? "dark bg-black text-gray-100" : "text-gray-900"}`}>
        <div className="p-4 flex flex-col items-center min-h-screen">
          <div className={`max-w-3xl w-full space-y-6 p-6 rounded-2xl shadow-xl ${darkMode ? "bg-gray-900" : "bg-white"}`}>
            <div className="flex justify-between items-center">
              <h1 className={`text-4xl font-bold text-center w-full ${darkMode ? "text-indigo-300" : "text-indigo-700"}`}>
                📐 Geometry AI Tutor
              </h1>
              <button
                className={`ml-2 p-3 rounded-lg transition ${
                  darkMode 
                    ? "bg-gray-700 hover:bg-gray-600 text-yellow-300" 
                    : "bg-indigo-100 hover:bg-indigo-200 text-gray-700"
                }`}
                onClick={toggleDarkMode}
              >
                {darkMode ? "🌞" : "🌙"}
              </button>
            </div>

            {!student ? (
              <div className="flex justify-center">
                <div className={`overflow-hidden rounded-lg h-[44px] w-[260px] ${darkMode ? "bg-gray-700" : "bg-gray-50"}`}>
                  <GoogleLogin
                    onSuccess={(res) => {
                      const decoded = jwt_decode(res.credential);
                      setStudent({ name: decoded.name, email: decoded.email });
                    }}
                    onError={() => console.log("Login Failed")}
                    theme={darkMode ? "filled_black" : "outline"}
                    size="large"
                    shape="rectangular"
                    width="260"
                    text="continue_with"
                    logo_alignment="left"
                  />
                </div>
              </div>
            ) : (
              <>
                <div className={`text-center text-lg ${darkMode ? "text-gray-300" : "text-gray-700"}`}>
                  Welcome, <strong>{student.name}</strong>
                </div>

                <div
                  ref={chatContainerRef}
                  className={`rounded-xl p-4 overflow-y-auto space-y-4 ${darkMode ? "bg-gray-800 border-gray-700" : "bg-white border-gray-200"} border chat-container`}
                  style={{ maxHeight: '60vh' }}
                >
                  {history.length === 0 && (
                    <div className={`text-center ${darkMode ? "text-gray-400" : "text-gray-600"}`}>
                      Hi! I'm <strong>Mr. Gilbot</strong>! Do you have any geometry-related questions?
                    </div>
                  )}

                  <AnimatePresence initial={false}>
                    {history.map((entry, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.4 }}
                        className="space-y-2"
                      >
                        {(entry.question?.trim() || entry.files?.length > 0) && (
                          <div className="flex justify-end gap-2 items-start">
                            <div className="flex flex-col items-end max-w-[75%] text-left">
                              {entry.files?.map((file, i) => (
                                <div key={i}>
                                  {file.url.match(/\.(jpeg|jpg|png|gif|png)$/i) ? (
                                    <img
                                      src={file.url}
                                      alt={file.name}
                                      className="max-h-32 rounded-lg border mt-1"
                                    />
                                  ) : (
                                    <a
                                      href={file.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className={`inline-block mb-1 px-3 py-2 rounded-lg text-sm transition ${darkMode ? "bg-gray-700 border-gray-600 text-indigo-300 hover:bg-gray-600" : "bg-indigo-50 border border-indigo-300 text-indigo-800 hover:bg-indigo-100"}`}
                                    >
                                      📎 {file.name}
                                    </a>
                                  )}
                                </div>
                              ))}
                              {entry.question?.trim() && (
                                <div className={`px-4 py-2 rounded-xl text-base whitespace-pre-wrap ${darkMode ? "bg-indigo-900 text-white border-gray-600" : "bg-blue-100 border border-blue-200"}`}>
                                  {entry.question}
                                </div>
                              )}
                            </div>
                            <div className="w-8 h-8 rounded-full bg-indigo-400 flex items-center justify-center text-white font-bold">
                              {student.name[0]}
                            </div>
                          </div>
                        )}
                        {entry.answer && (
                          <AIResponseBlock answer={entry.answer} darkMode={darkMode} />
                        )}
                      </motion.div>
                    ))}
                  </AnimatePresence>

                  {loading && (
                    <div className={`flex gap-2 items-center text-sm mt-2 ${darkMode ? "text-gray-400" : "text-gray-600"}`}>
                      <span className="animate-pulse">Thinking...</span>
                    </div>
                  )}
                </div>

                <div
                  className="mt-6 space-y-3"
                  ref={dropZoneRef}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                >
                  {files.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {files.map((file, i) => (
                        <div key={i} className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${darkMode ? "bg-gray-700 border-gray-600 text-indigo-300" : "bg-indigo-50 border border-indigo-300 text-indigo-800"}`}>
                          📎 {file.name}
                          <button onClick={() => removeFile(file.name)} className="text-red-500 hover:text-red-700">✕</button>
                        </div>
                      ))}
                    </div>
                  )}

                  <textarea
                    className={`w-full p-3 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-300 resize-none text-base text-left ${darkMode ? "bg-gray-700 text-white border-gray-600 placeholder-gray-400" : "bg-white border-gray-300 placeholder-gray-500"}`}
                    rows="3"
                    placeholder="Ask a geometry question..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={handleKeyPress}
                  />

                  <div className="flex items-center justify-between">
                    <label className="cursor-pointer">
                      <input
                        type="file"
                        multiple
                        onChange={(e) => handleFileUpload(e.target.files)}
                        className="hidden"
                      />
                      <span className={`inline-block px-4 py-2 rounded-md text-sm transition ${darkMode ? "bg-gray-700 text-indigo-300 hover:bg-gray-600" : "bg-indigo-100 text-indigo-800 hover:bg-indigo-200"}`}>
                        Choose File
                      </span>
                    </label>

                    <button
                      className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-lg shadow text-base"
                      onClick={handleAsk}
                      disabled={loading}
                    >
                      {loading ? "Thinking..." : "Ask Mr. Gilbot"}
                    </button>
                  </div>

                  <div className={`text-center text-sm mt-4 cursor-pointer ${darkMode ? "text-indigo-400" : "text-blue-600"}`} onClick={handleResetSession}>
                    Reset Session
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </GoogleOAuthProvider>
  );
}

export default App;