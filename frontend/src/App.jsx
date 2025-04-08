import React, { useState, useEffect, useRef } from "react";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import jwt_decode from "jwt-decode";
import { v4 as uuidv4 } from "uuid";
import { motion, AnimatePresence } from "framer-motion";
import "./App.css";
import AIResponseBlock from "./components/AIResponseBlock";

const CLIENT_ID = "781145386370-uau90m5m63tj5rroq7roheit3hjili6t.apps.googleusercontent.com";

function App() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState(null);
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [student, setStudent] = useState(null);
  const [history, setHistory] = useState(
    JSON.parse(localStorage.getItem("geometry_history")) || []
  );
  const chatContainerRef = useRef(null);

  useEffect(() => {
    let existing = localStorage.getItem("session_id");
    if (!existing) {
      existing = uuidv4();
      localStorage.setItem("session_id", existing);
    }
    setSessionId(existing);
  }, []);

  useEffect(() => {
    localStorage.setItem("geometry_history", JSON.stringify(history));
  }, [history]);

  useEffect(() => {
    chatContainerRef.current?.scrollTo({
      top: chatContainerRef.current.scrollHeight,
      behavior: "smooth"
    });
  }, [history, loading]);

  const extractGeoGebraLink = (text) => {
    const match = text.match(/GeoGebraID:\s*([a-zA-Z0-9]+)/);
    return match ? `https://www.geogebra.org/m/${match[1]}` : null;
  };

  const extractWolframURL = (text) => {
    const match = text.match(/WolframURL:\s*(https?:\/\/[^\s]+)/);
    return match ? match[1] : null;
  };

  const handleAsk = async () => {
    if (!student || !question.trim()) return;
    const previousQuestion = question.trim();
    setHistory((prev) => [...prev, { question: previousQuestion, image: image ? URL.createObjectURL(image) : null, answer: null }]);
    setQuestion("");
    setLoading(true);

    const formData = new FormData();
    formData.append("question", previousQuestion);
    formData.append("session_id", sessionId);
    formData.append("student_name", student.name);
    formData.append("student_email", student.email);
    if (image) formData.append("image", image);

    try {
      const res = await fetch("http://127.0.0.1:5051/api/ask", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResponse(data.response);
      setHistory((prev) =>
        prev.map((item, i) =>
          i === prev.length - 1 ? { ...item, answer: data.response.gpt } : item
        )
      );
    } catch (error) {
      console.error("Request failed:", error);
      setHistory((prev) =>
        prev.map((item, i) =>
          i === prev.length - 1 ? { ...item, answer: "Sorry, something went wrong." } : item
        )
      );
    }

    setImage(null);
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
    setResponse(null);
    setImage(null);
  };

  return (
    <GoogleOAuthProvider clientId={CLIENT_ID}>
      <div className="min-h-screen bg-gradient-to-br from-sky-50 to-indigo-100 p-4 flex flex-col items-center">
        <div className="max-w-3xl w-full space-y-6 text-[1.1rem] leading-relaxed">
          <h1 className="text-4xl font-bold text-center text-indigo-700">
            📐 Geometry AI Tutor
          </h1>

          {!student ? (
            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={(credentialResponse) => {
                  const decoded = jwt_decode(credentialResponse.credential);
                  setStudent({
                    name: decoded.name,
                    email: decoded.email,
                  });
                }}
                onError={() => console.log("Login Failed")}
                size="large"
                width="300"
              />
            </div>
          ) : (
            <>
              <div className="text-center text-gray-700 text-lg">
                Welcome, <strong>{student.name}</strong>
              </div>

              <div
                ref={chatContainerRef}
                className="bg-white rounded-xl p-4 shadow-md h-[65vh] overflow-y-auto space-y-4"
              >
                {history.length === 0 && (
                  <div className="text-center text-gray-600">
                    Hi! I'm <strong>Mr. Gilbot</strong>! Do you have any geometry-related questions?
                  </div>
                )}

                <AnimatePresence initial={false}>
                  {history.map((entry, index) => {
                    const geoLink = extractGeoGebraLink(entry.answer || "");
                    const wolframLink = extractWolframURL(entry.answer || "");
                    return (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.4 }}
                        className="space-y-2"
                      >
                        {entry.question && (
                          <div className="flex justify-end gap-2 items-start">
                            <div className="bg-indigo-100 px-4 py-2 rounded-xl text-base max-w-[75%]">
                              {entry.question}
                              {entry.image && (
                                <div className="mt-2">
                                  <img
                                    src={entry.image}
                                    alt="uploaded screenshot"
                                    className="rounded-lg border max-h-40 object-contain"
                                  />
                                </div>
                              )}
                            </div>
                            <div className="w-8 h-8 rounded-full bg-indigo-400 flex items-center justify-center text-white font-bold">
                              {student.name[0]}
                            </div>
                          </div>
                        )}

                        {entry.answer && (
                          <div className="flex gap-2 items-start">
                            <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white font-bold">
                              G
                            </div>
                            <div className="bg-white border px-4 py-3 rounded-xl text-base max-w-[75%] text-gray-800 text-left">
                              <AIResponseBlock answer={entry.answer} />
                              {wolframLink ? (
                                <div className="mt-4">
                                  <iframe
                                    src={wolframLink}
                                    width="100%"
                                    height="400"
                                    title="Wolfram Alpha Visual"
                                    className="rounded-md border"
                                  />
                                </div>
                              ) : geoLink ? (
                                <div className="mt-2">
                                  <a
                                    href={geoLink}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-600 underline"
                                  >
                                    📊 Explore on GeoGebra
                                  </a>
                                </div>
                              ) : null}
                            </div>
                          </div>
                        )}
                      </motion.div>
                    );
                  })}
                </AnimatePresence>

                {loading && (
                  <div className="flex gap-2 items-center text-sm text-gray-600 mt-2">
                    <span className="animate-pulse">Thinking...</span>
                  </div>
                )}
              </div>

              <div className="mt-6 space-y-3">
                <textarea
                  className="w-full p-3 border rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-300 resize-none text-base"
                  rows="3"
                  placeholder="Ask a geometry question..."
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={handleKeyPress}
                />
                <input
                  type="file"
                  onChange={(e) => setImage(e.target.files[0])}
                  className="block text-sm text-gray-600"
                />
                <div className="flex items-center gap-4">
                  <button
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-lg shadow text-base"
                    onClick={handleAsk}
                    disabled={loading}
                  >
                    {loading ? "Thinking..." : "Ask Mr. Gilbot"}
                  </button>
                  <button
                    className="bg-gray-200 hover:bg-gray-300 text-black px-4 py-2 rounded-lg shadow text-base"
                    onClick={handleResetSession}
                  >
                    Reset Session
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </GoogleOAuthProvider>
  );
}

export default App;
