"use client";
import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import { renderPrediction } from "@/utils/render-predictions";
const ObjectDetection = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isFile, setIsFile] = useState(false);
  const [fileSrc, setFileSrc] = useState(null);
  const [prediction, setPrediction] = useState([]);
  const [modelLog, setModelLog] = useState("");

  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const fileRef = useRef(null);

  // ✅ Handle File Upload and Send to Flask
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setFileSrc(URL.createObjectURL(file));
    setIsFile(true);
    setIsLoading(true);
    setPrediction([]);
    setModelLog("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/object-to-json", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      console.log("📢 Response from Flask:", data);

      const detectedLabels = data.detection_summary?.map((obj) =>
        obj.name.toLowerCase()
      ) || [];

      const messages = [];
      let isSomethingDetected = false;

      if (detectedLabels.includes("accident")) {
        messages.push("🚗 Accident Detected");
        isSomethingDetected = true;
      }

      if (
        detectedLabels.includes("robbery") ||
        detectedLabels.includes("theft") ||
        detectedLabels.includes("violence")
      ) {
        messages.push("🔫 Crime Detected");
        isSomethingDetected = true;
      }

      if (!isSomethingDetected) {
        messages.push("✅ No Accident or Crime Detected.");
      }

      setPrediction(messages);
    } catch (error) {
      console.error("🚨 Error uploading file:", error);
      setPrediction(["❌ Error processing file."]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mt-8">
      {isLoading ? (
        <div className="text-center text-blue-600 font-semibold animate-pulse">
          🔍 Detecting from uploaded file...
        </div>
      ) : (
        <>
          <div className="relative flex justify-center bg-gray-200 p-2 rounded-md">
            <canvas
              ref={canvasRef}
              className="absolute top-0 left-0 z-10 w-full lg:h-[720px]"
            />
            {!isFile ? (
              <Webcam
                ref={webcamRef}
                className="rounded-md w-full lg:h-[720px]"
              />
            ) : (
              <img
                ref={fileRef}
                src={fileSrc}
                alt="Uploaded"
                className="rounded-md w-full lg:h-[720px]"
              />
            )}
          </div>

          <input
            type="file"
            accept="image/*,video/*"
            onChange={handleFileUpload}
            className="mt-4 file:py-2 file:px-4 file:border-0 file:rounded-md file:bg-blue-600 file:text-white file:cursor-pointer"
          />

          {/* ✅ Show Predictions */}
          {prediction.length > 0 && (
            <div className="mt-4 text-lg text-center">
              <p
                className={
                  prediction.some(
                    (msg) =>
                      msg.includes("Accident") || msg.includes("Crime")
                  )
                    ? "text-red-600"
                    : "text-green-600"
                }
              >
                🚨 Prediction:{" "}
                {prediction.map((msg, idx) => (
                  <span key={idx}>
                    {msg}
                    {idx !== prediction.length - 1 ? " & " : ""}
                  </span>
                ))}
              </p>
            </div>
          )}

          {/* 🧠 Show Log from Model */}
          {modelLog && (
            <pre className="mt-4 text-sm bg-gray-100 p-3 rounded-md overflow-x-auto whitespace-pre-wrap border border-gray-300">
              🧠 Model Log Output:
              <br />
              {modelLog}
            </pre>
          )}
        </>
      )}
    </div>
  );
};

export default ObjectDetection;


