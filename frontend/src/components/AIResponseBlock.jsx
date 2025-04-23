import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import GeoGebraEmbed from "./GeoGebraEmbed";

const VideoEmbed = ({ videoId, title, url, darkMode }) => (
  <div className={`mt-4 border rounded-lg overflow-hidden shadow-sm ${darkMode ? "border-gray-700 bg-gray-800" : "border-gray-200 bg-gray-50"}`}>
    <div className="aspect-w-16 aspect-h-9">
      <iframe
        src={`https://www.youtube.com/embed/${videoId}`}
        title={title}
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
        className="w-full h-64"
      ></iframe>
    </div>
    <div className={`p-2 text-center text-sm ${darkMode ? "bg-gray-700 text-gray-300" : "bg-gray-100 text-gray-600"}`}>
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className={`underline inline-flex items-center gap-1 ${darkMode ? "text-blue-400 hover:text-blue-300" : "text-blue-600 hover:text-blue-700"}`}
      >
        Watch on Khan Academy ↗
      </a>
    </div>
  </div>
);

const AIResponseBlock = ({ answer, darkMode }) => {
  const [showVideoAlternates, setShowVideoAlternates] = useState(false);
  const [showGeoAlternates, setShowGeoAlternates] = useState(false);
  const [showLessonAlternates, setShowLessonAlternates] = useState(false);
  const [videoAlternates, setVideoAlternates] = useState([]);
  const [geoAlternates, setGeoAlternates] = useState([]);

  if (!answer || typeof answer === "string") {
    return (
      <div className="flex justify-start">
        <div className={`px-4 py-3 rounded-xl max-w-xl text-left border ${
          darkMode ? "bg-gray-700 text-white border-gray-600" : "bg-blue-100 border-blue-200"
        }`}>
          {answer}
        </div>
      </div>
    );
  }

  const {
    gpt,
    geogebra_id,
    geogebra_fallback,
    geogebra_alternates,
    wolfram_link,
    lesson_primary,
    lesson_alternates,
    khan_video
  } = answer;

  const processedText = wolfram_link
    ? `${gpt}\n\n[Here is an explanation from Wolfram Alpha](${wolfram_link})`
    : gpt;

  return (
    <div className="flex justify-start w-full">
      <div className="flex flex-col w-full max-w-xl">

        {/* GPT Response */}
        <div className={`px-4 py-3 rounded-xl text-base whitespace-pre-wrap text-left border ${
          darkMode ? "bg-gray-700 text-white border-gray-600" : "bg-blue-100 border-blue-200"
        }`}>
          <ReactMarkdown
            children={processedText}
            remarkPlugins={[remarkMath]}
            rehypePlugins={[rehypeKatex]}
            components={{
              a: ({ node, ...props }) => (
                <a
                  {...props}
                  className="text-blue-600 dark:text-blue-400 underline"
                  target="_blank"
                  rel="noopener noreferrer"
                />
              ),
            }}
          />
        </div>

        {/* Lesson Suggestion */}
        {lesson_primary && (
          <div className={`mt-2 text-sm ${darkMode ? "text-gray-300" : "text-gray-700"}`}>
            Check your notes for: <strong>{lesson_primary}</strong>
            {lesson_alternates?.length > 0 && !showLessonAlternates && (
              <div className="flex justify-center">
                <button
                  className="mt-2 text-sm underline text-blue-500"
                  onClick={() => setShowLessonAlternates(true)}
                >
                  Show other related lessons
                </button>
              </div>
            )}
            {showLessonAlternates && lesson_alternates.map((lesson, idx) => (
              <div key={idx} className="text-sm mt-1">
                {lesson}
              </div>
            ))}
          </div>
        )}

        {/* GeoGebra Section */}
        {(geogebra_id || geogebra_fallback) && (
          <div className="mt-2 w-full">
            {geogebra_id ? (
              <>
                <GeoGebraEmbed materialId={geogebra_id} darkMode={darkMode} />
                {geogebra_alternates?.length > 0 && !showGeoAlternates && (
                  <div className="flex justify-center">
                    <button
                      className="mt-2 text-sm underline text-blue-500"
                      onClick={() => setShowGeoAlternates(true)}
                    >
                      Show other GeoGebra activities
                    </button>
                  </div>
                )}
                {showGeoAlternates && geogebra_alternates.map((geo, idx) => (
                  <a
                    key={idx}
                    href={geo.url}
                    target="_blank"
                    rel="noreferrer"
                    className={`block text-sm mt-1 ${darkMode ? "text-blue-400" : "text-blue-600"}`}
                  >
                    {geo.title || `GeoGebra Activity ${idx + 1}`} ↗
                  </a>
                ))}
              </>
            ) : (
              <div className={`p-2 rounded-lg ${darkMode ? "bg-gray-700" : "bg-gray-50"}`}>
                <a
                  href={geogebra_fallback}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`inline-flex items-center gap-1 ${darkMode ? "text-blue-400 hover:text-blue-300" : "text-blue-600 hover:text-blue-700"}`}
                >
                  <span>Explore on GeoGebra</span>
                  <span>↗</span>
                </a>
              </div>
            )}
          </div>
        )}

        {/* Khan Academy Video Section */}
        {khan_video && (
          <>
            <VideoEmbed
              videoId={khan_video.primary?.video_id || khan_video.video_id}
              title={khan_video.primary?.title || khan_video.title}
              url={khan_video.primary?.url || khan_video.url}
              darkMode={darkMode}
            />
            {khan_video.alternates?.length > 0 && !showVideoAlternates && (
              <div className="flex justify-center">
                <button
                  className="mt-2 text-sm underline text-blue-500"
                  onClick={() => setShowVideoAlternates(true)}
                >
                  Show other video suggestions
                </button>
              </div>
            )}
            {showVideoAlternates && khan_video.alternates.map((vid, idx) => (
              <a
                key={idx}
                href={vid.url}
                target="_blank"
                rel="noreferrer"
                className={`block text-sm mt-1 ${darkMode ? "text-blue-400" : "text-blue-600"}`}
              >
                {vid.title} ↗
              </a>
            ))}
          </>
        )}

      </div>
    </div>
  );
};

export default AIResponseBlock;
