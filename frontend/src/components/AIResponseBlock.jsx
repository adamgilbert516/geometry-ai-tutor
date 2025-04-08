import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

export default function AIResponseBlock({ answer }) {
  if (!answer) return null;

  return (
    <div className="bg-white border px-6 py-4 rounded-xl text-base max-w-[75%] text-gray-800 text-left leading-relaxed space-y-2 overflow-x-auto">
      <ReactMarkdown
        children={answer}
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
        }}
      />
    </div>
  );
}


