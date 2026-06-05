"use client";
import React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { CheckCircleIcon, StarIcon } from "lucide-react";
import { motion } from "motion/react";

type FREQUENCY = "monthly" | "yearly";
const frequencies: FREQUENCY[] = ["monthly", "yearly"];

interface Plan {
  name: string;
  info: string;
  price: {
    monthly: number;
    yearly: number;
  };
  originalPrice?: {
    monthly: number;
    yearly: number;
  };
  features: {
    text: string;
    tooltip?: string;
  }[];
  btn: {
    text: string;
    href: string;
  };
  highlighted?: boolean;
}

interface PricingSectionProps extends React.ComponentProps<"div"> {
  plans: Plan[];
  heading: React.ReactNode;
  description?: string;
}

const cardVariants = {
  hidden: { opacity: 0, y: 40, scale: 0.95 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { delay: 0.1 + i * 0.12, duration: 0.7, ease: [0.34, 1.56, 0.64, 1] as const },
  }),
};

const hoverSpring = {
  type: "spring" as const,
  stiffness: 200,
  damping: 12,
};

export function PricingSection({ plans, heading, description, ...props }: PricingSectionProps) {
  const [frequency, setFrequency] = React.useState<FREQUENCY>("monthly");

  return (
    <div className={cn("flex w-full flex-col items-center justify-center space-y-5 p-4", props.className)} {...props}>
      <motion.div
        className="mx-auto max-w-xl space-y-2"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
      >
        <h2 className="text-center text-4xl font-bold tracking-[-0.02em] md:text-5xl lg:text-6xl text-[#1D1D1F]">
          {heading}
        </h2>
        {description && <p className="text-center text-base text-gray-400">{description}</p>}
      </motion.div>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        transition={{ delay: 0.15, duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
      >
        <PricingFrequencyToggle frequency={frequency} setFrequency={setFrequency} />
      </motion.div>
      <div className="mx-auto grid w-full max-w-3xl grid-cols-1 gap-4 md:grid-cols-2">
        {plans.map((plan, i) => (
          <PricingCard plan={plan} key={plan.name} frequency={frequency} index={i} />
        ))}
      </div>
    </div>
  );
}

type PricingFrequencyToggleProps = React.ComponentProps<"div"> & {
  frequency: FREQUENCY;
  setFrequency: React.Dispatch<React.SetStateAction<FREQUENCY>>;
};

export function PricingFrequencyToggle({ frequency, setFrequency, ...props }: PricingFrequencyToggleProps) {
  return (
    <div className={cn("mx-auto flex w-fit rounded-full border border-gray-200/60 bg-white/60 p-1", props.className)} {...props}>
      {frequencies.map((freq) => (
          <button
            key={freq}
            onClick={() => setFrequency(freq)}
            className="relative px-5 py-1.5 text-sm capitalize"
          >
            <span className={cn("relative z-10", frequency === freq ? "text-white" : "text-[#1D1D1F]")}>
              {freq === "monthly" ? "Mensal" : "Anual"}
            </span>
            {frequency === freq && (
              <motion.span
                layoutId="frequency"
                transition={{ type: "spring", duration: 0.5, bounce: 0.3 }}
                className="absolute inset-0 z-0 rounded-full bg-[#1D1D1F]"
              />
            )}
          </button>
        ))}
    </div>
  );
}

type PricingCardProps = React.ComponentProps<"div"> & {
  plan: Plan;
  frequency?: FREQUENCY;
  index?: number;
};

export function PricingCard({ plan, className, frequency = frequencies[0], index = 0 }: PricingCardProps) {
  const navigate = useNavigate();

  return (
    <motion.div
      className={cn(
        "relative flex w-full flex-col rounded-3xl border border-gray-200/40 bg-white/60 backdrop-blur-xl",
        plan.highlighted && "ring-[1.5px] ring-[#1D1D1F]/60",
        className,
      )}
      variants={cardVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
      custom={index}
      whileHover={{ y: -4, boxShadow: "0 12px 40px rgba(0,0,0,0.06)" }}
      transition={hoverSpring}
    >
      <div className={cn("rounded-t-3xl border-b border-gray-200/40 p-4", plan.highlighted && "bg-gray-50/80")}>
        <div className="absolute right-3 top-3 z-10 flex items-center gap-2">
          {plan.highlighted && (
            <motion.span
              className="flex items-center gap-1 rounded-full border border-gray-200/60 bg-white/80 px-3 py-1 text-xs font-medium text-[#1D1D1F]"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 + index * 0.12, duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
            >
              <StarIcon className="h-3 w-3 fill-current" />
              Popular
            </motion.span>
          )}
          {frequency === "yearly" && plan.price.monthly > 0 && (
            <motion.span
              className="flex items-center gap-1 rounded-full bg-[#22c55e]/10 px-3 py-1 text-xs font-medium text-[#22c55e]"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4 + index * 0.12, duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
            >
              {Math.round(
                ((plan.price.monthly * 12 - plan.price.yearly) / plan.price.monthly / 12) * 100,
              )}% off
            </motion.span>
          )}
        </div>
        <div className="text-lg font-semibold text-[#1D1D1F]">{plan.name}</div>
        <p className="text-sm text-gray-400">{plan.info}</p>
        <h3 className="mt-2 flex items-end gap-2">
          {plan.originalPrice && (
            <span className="text-lg text-gray-300 line-through decoration-gray-300">
              R$ {frequency === "monthly" ? plan.originalPrice.monthly : plan.originalPrice.yearly}
            </span>
          )}
          <motion.span
            className="text-4xl font-light tracking-tight text-[#1D1D1F]"
            key={frequency}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, ease: [0.34, 1.56, 0.64, 1] }}
          >
            {frequency === "monthly" ? `R$ ${plan.price.monthly}` : `R$ ${plan.price.yearly}`}
          </motion.span>
          <span className="text-sm text-gray-400">
            {plan.name !== "Free" ? (frequency === "monthly" ? "/mês" : "/ano") : ""}
          </span>
        </h3>
      </div>
      <div className={cn("flex-1 space-y-4 px-4 py-6 text-sm", plan.highlighted && "bg-gray-50/40")}>
        {plan.features.map((feature, fi) => (
          <motion.div
            key={fi}
            className="flex items-center gap-2"
            initial={{ opacity: 0, x: -10 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 + fi * 0.06, duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
          >
            <CheckCircleIcon className="h-4 w-4 text-[#22c55e] shrink-0" />
            <TooltipProvider>
              <Tooltip delayDuration={0}>
                <TooltipTrigger asChild>
                  <span className={cn("text-gray-500", feature.tooltip && "cursor-pointer border-b border-dashed border-gray-300")}>
                    {feature.text}
                  </span>
                </TooltipTrigger>
                {feature.tooltip && (
                  <TooltipContent className="rounded-xl border-gray-200/60 bg-white/90 backdrop-blur-xl text-gray-500 text-xs">
                    <p>{feature.tooltip}</p>
                  </TooltipContent>
                )}
              </Tooltip>
            </TooltipProvider>
          </motion.div>
        ))}
      </div>
      <div className={cn("mt-auto w-full border-t border-gray-200/40 p-3", plan.highlighted && "bg-gray-50/80")}>
        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} transition={{ type: "spring", stiffness: 300, damping: 15 }}>
          <Button
            onClick={() => navigate(plan.btn.href)}
            className={cn(
              "w-full h-12 rounded-full text-sm font-semibold",
              plan.highlighted
                ? "bg-[#1D1D1F] text-white hover:bg-[#1D1D1F]/80"
                : "border border-gray-200 bg-white text-[#1D1D1F] hover:bg-gray-50 shadow-sm",
            )}
          >
            {plan.btn.text}
          </Button>
        </motion.div>
      </div>
    </motion.div>
  );
}
