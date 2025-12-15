"use client";

import { useState, useRef, useCallback } from "react";
import { createPortal } from "react-dom";

interface TooltipHeaderProps {
    label: string;
    tooltip: string | undefined;
    sortIndicator?: React.ReactNode;
    onClick?: () => void;
    className?: string;
}

export function TooltipHeader({ label, tooltip, sortIndicator, onClick, className = "" }: TooltipHeaderProps) {
    const [showTooltip, setShowTooltip] = useState(false);
    const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
    const thRef = useRef<HTMLTableCellElement>(null);

    const handleMouseEnter = useCallback(() => {
        if (thRef.current && tooltip) {
            const rect = thRef.current.getBoundingClientRect();
            setTooltipPos({
                x: rect.left + rect.width / 2,
                y: rect.top - 8
            });
            setShowTooltip(true);
        }
    }, [tooltip]);

    const handleMouseLeave = useCallback(() => {
        setShowTooltip(false);
    }, []);

    return (
        <th
            ref={thRef}
            onClick={onClick}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            className={className}
        >
            {label}
            {sortIndicator}
            {showTooltip && tooltip && typeof document !== 'undefined' && createPortal(
                <div
                    style={{
                        position: 'fixed',
                        zIndex: 99999,
                        left: tooltipPos.x,
                        top: tooltipPos.y,
                        transform: 'translate(-50%, -100%)',
                        padding: '8px 12px',
                        backgroundColor: '#1a1a1a',
                        color: 'white',
                        fontSize: '12px',
                        fontWeight: 400,
                        letterSpacing: 'normal',
                        textTransform: 'none',
                        borderRadius: '8px',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                        whiteSpace: 'nowrap',
                        pointerEvents: 'none'
                    }}
                >
                    {tooltip}
                    <div
                        style={{
                            position: 'absolute',
                            left: '50%',
                            transform: 'translateX(-50%)',
                            top: '100%',
                            width: 0,
                            height: 0,
                            borderLeft: '6px solid transparent',
                            borderRight: '6px solid transparent',
                            borderTop: '6px solid #1a1a1a'
                        }}
                    />
                </div>,
                document.body
            )}
        </th>
    );
}
