import { useEffect, useState } from "react";
import { motion } from "motion/react";

interface SkeletonShimmerProps {
  shimmerDuration?: number;
  loadDelay?: number;
}

export function SkeletonShimmer({ shimmerDuration = 3.1 }: SkeletonShimmerProps) {
  return (
    <div className="fixed inset-0 z-[100] flex flex-col gap-6 bg-[#F5F5F7] p-8">
      {/* Navbar skeleton */}
      <div className="flex items-center justify-between">
        <div className="skeleton-shimmer h-4 w-20 rounded-full" style={{ animationDuration: `${shimmerDuration}s` }} />
        <div className="flex gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton-shimmer h-3 w-12 rounded-full" style={{ animationDuration: `${shimmerDuration}s` }} />
          ))}
          <div className="skeleton-shimmer h-8 w-28 rounded-full" style={{ animationDuration: `${shimmerDuration}s` }} />
        </div>
      </div>

      {/* Hero skeleton */}
      <div className="flex flex-1 flex-col items-center justify-center gap-6">
        <div className="skeleton-shimmer h-16 w-[500px] max-w-full rounded-xl" style={{ animationDuration: `${shimmerDuration}s` }} />
        <div className="skeleton-shimmer h-16 w-[400px] max-w-full rounded-xl" style={{ animationDuration: `${shimmerDuration}s` }} />
        <div className="skeleton-shimmer mt-4 h-4 w-[300px] max-w-full rounded-full" style={{ animationDuration: `${shimmerDuration}s` }} />
        <div className="skeleton-shimmer mt-6 h-12 w-40 rounded-full" style={{ animationDuration: `${shimmerDuration}s` }} />
      </div>

      {/* Cards skeleton */}
      <div className="flex justify-center gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="skeleton-shimmer h-40 w-56 rounded-2xl" style={{ animationDuration: `${shimmerDuration}s`, animationDelay: `${i * 0.1}s` }} />
        ))}
      </div>
    </div>
  );
}

export function ContentReveal({ children, loadDelay = 1200, shimmerDuration = 3.1 }: { children: React.ReactNode; loadDelay?: number; shimmerDuration?: number }) {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setShow(true), loadDelay);
    return () => clearTimeout(t);
  }, [loadDelay]);

  return (
    <>
      {!show && <SkeletonShimmer shimmerDuration={shimmerDuration} />}
      <motion.div
        initial={{ opacity: 0 }}
        animate={show ? { opacity: 1 } : { opacity: 0 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
      >
        {children}
      </motion.div>
    </>
  );
}
