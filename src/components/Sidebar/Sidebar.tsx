import React from "react";
import styles from "./Sidebar.module.css";

interface SidebarProps {
  onSelect: (key: string) => void;
}

const menuItems = [
  { name: "Dashboard", key: "dashboard" },
  { name: "Processos", key: "processos" },
  { name: "Drivers", key: "drivers" },
  { name: "Configurações", key: "config" },
];

export default function Sidebar({ onSelect }: SidebarProps) {
  const [active, setActive] = React.useState("dashboard");

  const handleClick = (key: string) => {
    setActive(key);
    onSelect(key);
  };

  return (
    <div className={styles.sidebar}>
      <div className={styles.sidebarTitle}>MachineMonitorZ</div>

      {menuItems.map((item) => (
        <div
          key={item.key}
          className={`${styles.menuItem} ${active === item.key ? styles.active : ""}`}
          onClick={() => handleClick(item.key)}
        >
          {item.name}
        </div>
      ))}
    </div>
  );
}
