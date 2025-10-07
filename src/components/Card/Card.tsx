import React from "react";
import styles from "./Card.module.css";

interface Props {
  title: string;
  value: string;
  color?: string; // cor dinâmica
}

export default function MetricCard({ title, value, color = "#3b82f6" }: Props) {
  return (
    <div
      className={styles.card}
      style={{ "--border-color": color, "--text-color": color } as React.CSSProperties}
    >
      <div className={styles.cardContent}>
        <span className={styles.cardTitle}>{title}</span>
        <span className={styles.cardValue}>{value}</span>
      </div>
    </div>
  );
}
