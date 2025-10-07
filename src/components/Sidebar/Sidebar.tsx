import styles from "./Sidebar.module.css";

const menuItems = ["Dashboard", "Processos", "Drivers", "Configurações"];

export default function Sidebar() {
  return (
    <div className={styles.sidebar}>
      <div className={styles.sidebarTitle}>MachineMonitorZ</div>

      {menuItems.map((item) => (
        <div key={item} className={styles.menuItem}>
          {item}
        </div>
      ))}
    </div>
  );
}
