import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

export default function AIResponseBlock({ answer }) {
  if (!answer) return null;

  // Extract and clean WolframURL
  const wolframMatch = answer.match(/\[Here is an explanation from Wolfram Alpha\]\((https?:\/\/[^\s]+)\)/);
  const wolframURL = wolframMatch ? wolframMatch[1] : null;

  // Strip any raw label preceding Wolfram links
  let cleanedText = answer
    .replace(/WolframAlpha[-\w]*:?/, "")
    .replace(/\[.*?\]\(https:\/\/www\.wolframalpha\.com\/input\?i=[^)]+\)/g, "")
    // Strip any markdown link GPT might have hallucinated
    .replace(/\[Here is an explanation from Wolfram Alpha\]\(https?:\/\/[^\s]+?\)/g, "")
    .trim();

  return (
    <div className="bg-white border px-6 py-4 rounded-xl text-base max-w-[75%] text-gray-800 text-left leading-relaxed space-y-2 overflow-x-auto">
      <ReactMarkdown
        children={cleanedText}
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          p: ({ children }) => <p className="mb-3 text-base">{children}</p>,
          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
          em: ({ children }) => <em className="italic">{children}</em>,
          ul: ({ children }) => <ul className="list-disc list-inside ml-4">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside ml-4">{children}</ol>,
          li: ({ children }) => <li className="mb-1">{children}</li>,
          code: ({ children }) => (
            <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono">{children}</code>
          ),
          pre: ({ children }) => <pre className="bg-gray-100 p-2 rounded overflow-auto">{children}</pre>,
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 underline hover:text-blue-800 transition"
            >
              {children}
            </a>
          ),
        }}
      />
    </div>
  );
}
