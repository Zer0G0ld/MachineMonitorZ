import { Flex, Spinner, Text, Center } from "@chakra-ui/react";
import Sidebar from "./components/Sidebar/Sidebar";
import Dashboard from "./components/Dashboard/Dashboard";
import { useMetrics } from "./hooks/useMetrics"; // ✅ importa o hook
import type { Metric } from "./hooks/useMetrics"; // ✅ importa o tipo (só pra tipagem)

export default function App() {
  const { metrics, loading, error } = useMetrics(3000);

  if (loading) {
    return (
      <Center h="100vh" bg="gray.900" flexDir="column">
        <Spinner size="xl" color="blue.400" />
        <Text mt={4} color="gray.300">
          Carregando métricas...
        </Text>
      </Center>
    );
  }

  if (error) {
    return (
      <Center h="100vh" bg="gray.900" flexDir="column">
        <Text color="red.400" fontWeight="bold">
          Erro ao carregar métricas
        </Text>
        <Text color="gray.400" fontSize="sm">
          {error}
        </Text>
      </Center>
    );
  }

  return (
    <Flex h="100vh" bg="gray.900" color="white">
      <Sidebar />
      {/* ✅ agora Dashboard recebe as métricas corretamente */}
      <Dashboard metrics={metrics as Metric} />
    </Flex>
  );
}
