import React from "react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import GeoGebraEmbed from "./GeoGebraEmbed";

const AIResponseBlock = ({ answer }) => {
  if (!answer || typeof answer === "string") {
    return (
      <div className="chat chat-start">
        <div className="chat-bubble ai-bubble">{answer}</div>
      </div>
    );
  }

  const { gpt, geogebra_id, geogebra_fallback, wolfram_link, lesson_found } = answer;

  const sanitizedGpt = lesson_found === false
    ? gpt.replace(/(please (see|refer to).*?lesson.*?)\n?/i, "")
    : gpt;

  const processedText = wolfram_link
    ? `${sanitizedGpt}\n\n[Here is an explanation from Wolfram Alpha](${wolfram_link})`
    : sanitizedGpt;

  const hasGeoGebraPrompt = /let me show you.*diagram|interactive activity|this might be easier.*picture|explore this concept|try an interactive tool/i.test(gpt);

  return (
    <div className="chat chat-start">
      <div className="chat-bubble bg-blue-100 text-black dark:bg-white dark:text-black max-w-xl whitespace-pre-wrap text-left">
        <ReactMarkdown
          children={processedText}
          remarkPlugins={[remarkMath]}
          rehypePlugins={[rehypeKatex]}
          components={{
            a: ({ node, ...props }) => (
              <a
                {...props}
                className="text-blue-600 underline"
                target="_blank"
                rel="noopener noreferrer"
              />
            ),
          }}
        />

        {hasGeoGebraPrompt && geogebra_id && (
          <GeoGebraEmbed materialId={geogebra_id} />
        )}

        {hasGeoGebraPrompt && !geogebra_id && geogebra_fallback && (
          <div className="mt-4 text-sm text-blue-600 underline text-center">
            <a href={geogebra_fallback} target="_blank" rel="noopener noreferrer">
              Explore on GeoGebra ↗
            </a>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIResponseBlock;
