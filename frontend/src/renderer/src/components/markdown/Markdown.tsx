import { lazy, Suspense } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { cn } from "@/lib/utils";

// Code-splitting : react-syntax-highlighter et mermaid sont lourds. On ne les
// charge que lorsqu'un message contient réellement un bloc de code / diagramme.
const CodeBlock = lazy(() =>
  import("./CodeBlock").then((m) => ({ default: m.CodeBlock })),
);
const Mermaid = lazy(() =>
  import("./Mermaid").then((m) => ({ default: m.Mermaid })),
);

/** Repli affiché pendant le chargement du composant lourd : le code brut. */
function RawCode({ value }: { value: string }) {
  return (
    <pre className="my-2 overflow-x-auto rounded-md border bg-muted p-3 text-xs">
      {value}
    </pre>
  );
}

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
                return (
                  <Suspense fallback={<RawCode value={value} />}>
                    <Mermaid chart={value} />
                  </Suspense>
                );
              }
              return (
                <Suspense fallback={<RawCode value={value} />}>
                  <CodeBlock language={language} value={value} />
                </Suspense>
              );
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
