import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { forwardRef, type ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 border-2 border-ink font-sans text-sm font-bold uppercase transition-[transform,box-shadow,background-color] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-cyan/40 disabled:pointer-events-none disabled:opacity-45",
  {
    variants: {
      variant: {
        default: "bg-orange text-ink shadow-hard hover:-translate-y-0.5 active:translate-x-1 active:translate-y-1 active:shadow-none",
        outline: "bg-paper text-ink shadow-hard hover:-translate-y-0.5 active:translate-x-1 active:translate-y-1 active:shadow-none",
        ink: "bg-ink text-paper shadow-hard-cyan hover:-translate-y-0.5 active:translate-x-1 active:translate-y-1 active:shadow-none",
        paper: "bg-paper text-ink shadow-hard hover:-translate-y-0.5 active:translate-x-1 active:translate-y-1 active:shadow-none",
        ghost: "border-transparent bg-transparent text-ink hover:bg-ink/5",
      },
      size: {
        default: "h-11 px-4",
        sm: "h-9 px-3 text-xs",
        icon: "size-10 p-0",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  },
);

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  };

const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { className, variant, size, asChild = false, ...props },
  ref,
) {
  const Comp = asChild ? Slot : "button";
  return <Comp ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />;
});

export { Button, buttonVariants };