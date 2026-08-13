import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { cn } from "@/lib/utils";
import { CodeBlock } from "./CodeBlock";
import { Mermaid } from "./Mermaid";

export function Markdown({ content }: { content: string }) {
  return (
    <div
      className={cn(
        "prose prose-sm dark:prose-invert max-w-none",
        // on neutralise le style prose des blocs de code : CodeBlock/Mermaid gèrent le leur
        "prose-pre:m-0 prose-pre:bg-transparent prose-pre:p-0",
      )}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // évite un <pre> parasite autour de nos propres blocs
          pre: ({ children }) => <>{children}</>,
          code({ className, children, ...props }) {
            const match = /language-(\w+)/.exec(className ?? "");
            const value = String(children).replace(/\n$/, "");
            if (match) {
              const language = match[1];
              if (language === "mermaid") {
                return <Mermaid chart={value} />;
              }
              return <CodeBlock language={language} value={value} />;
            }
            return (
              <code
                className="rounded bg-muted px-1 py-0.5 text-[0.85em]"
                {...props}
              >
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
