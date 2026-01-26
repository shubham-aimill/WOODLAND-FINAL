import { useState } from "react";
import { MessageCircle } from "lucide-react";
import { ChatWindow } from "./ChatWindow";

export const FloatingBot = () => {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Floating trigger button */}
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="fixed bottom-6 right-4 sm:bottom-7 sm:right-7 z-40 h-14 w-14 sm:h-16 sm:w-16 rounded-full bg-primary text-primary-foreground shadow-xl flex items-center justify-center border border-primary/40 hover:shadow-2xl hover:scale-105 active:scale-95 transition-transform transition-shadow duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background"
        aria-label={open ? "Close assistant" : "Open assistant"}
      >
        <span className="absolute inset-0 rounded-full bg-primary/40 blur-xl opacity-40 pointer-events-none" />
        <MessageCircle className="relative h-7 w-7 sm:h-8 sm:w-8" />
      </button>

      {/* Chat window */}
      <ChatWindow open={open} onClose={() => setOpen(false)} />
    </>
  );
};

