// import {
//   createContext,
//   useCallback,
//   useContext,
//   useState,
//   ReactNode,
// } from "react";

// export type ChatRole = "user" | "assistant";

// export interface ChatMessage {
//   id: string;
//   role: ChatRole;
//   content: string;
//   timestamp: Date;
// }

// interface ChatContextValue {
//   messages: ChatMessage[];
//   input: string;
//   isSending: boolean;
//   setInput: (value: string) => void;
//   sendMessage: () => Promise<void>;
//   clearConversation: () => void;
// }

// const ChatContext = createContext<ChatContextValue | undefined>(undefined);

// interface ChatProviderProps {
//   children: ReactNode;
// }

// export const ChatProvider = ({ children }: ChatProviderProps) => {
//   const [messages, setMessages] = useState<ChatMessage[]>([]);
//   const [input, setInput] = useState("");
//   const [isSending, setIsSending] = useState(false);

//   const clearConversation = useCallback(() => {
//     setMessages([]);
//     setInput("");
//     setIsSending(false);
//   }, []);

//    const sendMessage = useCallback(async () => {
//   if (!input.trim() || isSending) return;

//   const text = input.trim();

//   const userMessage: ChatMessage = {
//     id: `${Date.now()}-user`,
//     role: "user",
//     content: text,
//     timestamp: new Date(),
//   };

//   setMessages((prev) => [...prev, userMessage]);
//   setInput("");
//   setIsSending(true);

//   try {
//     const res = await fetch("http://localhost:5052/api/chat", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//       },
//       // credentials: "include",   // 🔥 THIS LINE FIXES EVERYTHING
//       body: JSON.stringify({ question: text }),
//     });


//     const data = await res.json();

//     const assistantMessage: ChatMessage = {
//       id: `${Date.now()}-assistant`,
//       role: "assistant",
//       content: data.summary ?? "⚠️ No response from server.",
//       timestamp: new Date(),
//     };

//     setMessages((prev) => [...prev, assistantMessage]);
//   } catch (error) {
//     const errorMessage: ChatMessage = {
//       id: `${Date.now()}-assistant-error`,
//       role: "assistant",
//       content: "❌ Unable to reach server. Is the backend running?",
//       timestamp: new Date(),
//     };

//     setMessages((prev) => [...prev, errorMessage]);
//   } finally {
//     setIsSending(false);
//   }
// }, [input, isSending]);


//   return (
//     <ChatContext.Provider
//       value={{
//         messages,
//         input,
//         isSending,
//         setInput,
//         sendMessage,
//         clearConversation,
//       }}
//     >
//       {children}
//     </ChatContext.Provider>
//   );
// };

// export const useChat = () => {
//   const ctx = useContext(ChatContext);
//   if (!ctx) {
//     throw new Error("useChat must be used within a ChatProvider");
//   }
//   return ctx;
// };






import {
  createContext,
  useCallback,
  useContext,
  useState,
  ReactNode,
} from "react";

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  timestamp: Date;
  chart?: string | null;
}

interface ChatContextValue {
  messages: ChatMessage[];
  input: string;
  isSending: boolean;
  setInput: (value: string) => void;
  sendMessage: () => Promise<void>;
  clearConversation: () => void;
}

const ChatContext = createContext<ChatContextValue | undefined>(undefined);

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider = ({ children }: ChatProviderProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);

  const clearConversation = useCallback(() => {
    setMessages([]);
    setInput("");
    setIsSending(false);
  }, []);

  const sendMessage = useCallback(async () => {
    if (!input.trim() || isSending) return;

    // -----------------------------
    // 1. Push user message
    // -----------------------------
    const text = input.trim();

    setMessages(prev => [
      ...prev,
      {
        id: `${Date.now()}-user`,
        role: "user",
        content: text,
        timestamp: new Date(),
      },
    ]);

    setInput("");
    setIsSending(true);

    try {
      // -----------------------------
      // 2. Call backend
      // -----------------------------
      const res = await fetch("http://localhost:5052/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text }),
      });

      const data = await res.json();

      const chart =
        data.viz && data.mime?.startsWith("image/")
          ? `data:${data.mime};base64,${data.viz}`
          : null;

      // -----------------------------
      // 3. FORMAT RESPONSE ← YOUR CODE GOES HERE
      // -----------------------------
      let content = (data.summary ?? "").trim();

      if (content && !content.endsWith(".")) {
        content += ".";
      }

      if (Array.isArray(data.data) && data.data.length > 0) {
        content += "\n\n📊 Detailed Results:\n";

        content += data.data
          .map((row: any) => {
            if (row.store_id && row["SUM(actual_sales_units)"] !== undefined) {
              return `• ${row.store_id}: ${row["SUM(actual_sales_units)"]} units`;
            }

            return `• ${Object.entries(row)
              .map(([k, v]) => `${k}: ${v}`)
              .join(", ")}`;
          })
          .join("\n");
      }

      // -----------------------------
      // 4. Push assistant message
      // -----------------------------
      setMessages(prev => [
        ...prev,
        {
          id: `${Date.now()}-assistant`,
          role: "assistant",
          content,
          chart,
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      setMessages(prev => [
        ...prev,
        {
          id: `${Date.now()}-assistant-error`,
          role: "assistant",
          content: "❌ Unable to reach server. Is the backend running?",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }, [input, isSending]);

  return (
    <ChatContext.Provider
      value={{
        messages,
        input,
        isSending,
        setInput,
        sendMessage,
        clearConversation,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const ctx = useContext(ChatContext);
  if (!ctx) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return ctx;
};