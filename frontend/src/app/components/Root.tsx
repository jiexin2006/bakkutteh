import { Outlet } from "react-router";
import { motion, AnimatePresence } from "motion/react";

export function Root() {
  return (
    <div className="min-h-screen bg-[#121418] text-foreground overflow-hidden">
      <AnimatePresence mode="wait">
        <Outlet />
      </AnimatePresence>
    </div>
  );
}
