import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { renderToString } from "katex";

export default function AIResponseBlock({ answer }) {
  if (!answer) return null;

  const safeRender = (latex, displayMode = false) => {
    try {
      return renderToString(String(latex), {
        displayMode,
        throwOnError: false,
      });
    } catch (err) {
      console.error("KaTeX rendering error:", err);
      return latex;
    }
  };

  return (
    <div className="bg-white border px-6 py-4 rounded-xl text-base max-w-[75%] text-gray-800 text-left leading-relaxed space-y-2 overflow-x-auto">
      <ReactMarkdown
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
            <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono">
              {children}
            </code>
          ),
          pre: ({ children }) => (
            <pre className="bg-gray-100 p-3 rounded overflow-auto text-sm">
              {children}
            </pre>
          ),
          math: ({ value }) => (
            <div
              className="my-4 text-center text-lg overflow-x-auto"
              dangerouslySetInnerHTML={{ __html: safeRender(value, true) }}
            />
          ),
          inlineMath: ({ value }) => (
            <span
              className="text-indigo-700"
              dangerouslySetInnerHTML={{ __html: safeRender(value, false) }}
            />
          ),
        }}
      >
        {answer}
      </ReactMarkdown>
    </div>
  );
}
