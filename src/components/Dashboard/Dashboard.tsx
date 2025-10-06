import { Box, Heading, SimpleGrid, Text, Flex } from "@chakra-ui/react";
import MetricCard from "../Card/Card";
import type { Metric } from "../../hooks/useMetrics";

interface DashboardProps {
  metrics: Metric | null;
}

export default function Dashboard({ metrics }: DashboardProps) {
  const cpu = metrics?.cpu?.usage_pct[0]?.toFixed(1) ?? "0";
  const memory = metrics?.memory?.used_pct?.toFixed(1) ?? "0";
  const disk = metrics?.disks?.[0]?.used_pct?.toFixed(1) ?? "0";

  return (
    <Box flex="1" p={8} overflowY="auto" bg="gray.900">
      <Flex justify="space-between" align="center" mb={6}>
        <Box>
          <Heading size="lg" color="blue.300">
            Painel de Monitoramento
          </Heading>
          <Text color="gray.400" fontSize="sm">
            Atualizado em {new Date(metrics?.timestamp ?? Date.now()).toLocaleTimeString()}
          </Text>
        </Box>
      </Flex>

      <Box h="1px" bg="gray.700" my={8} />

      {/* Aqui o spacing agora é único */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={6}>
        <MetricCard title="CPU" value={`${cpu}%`} color="blue.400" />
        <MetricCard title="Memória" value={`${memory}%`} color="green.400" />
        <MetricCard title="Disco" value={`${disk}%`} color="orange.400" />
      </SimpleGrid>

      <Box mt={10}>
        <Heading size="md" color="gray.300" mb={4}>
          Processos Principais
        </Heading>
        {metrics?.top_processes?.length ? (
          <Box
            bg="gray.800"
            p={4}
            borderRadius="md"
            shadow="md"
            border="1px solid"
            borderColor="gray.700"
          >
            {metrics.top_processes.slice(0, 5).map((p, i) => (
              <Flex
                key={i}
                justify="space-between"
                py={2}
                borderBottom={i !== 4 ? "1px solid" : "none"}
                borderColor="gray.700"
              >
                <Text color="gray.300" truncate>
                  {p.name}
                </Text>
                <Text color="blue.300" fontWeight="medium">
                  {p.cpu_percent.toFixed(1)}%
                </Text>
              </Flex>
            ))}
          </Box>
        ) : (
          <Text color="gray.500">Nenhum processo listado.</Text>
        )}
      </Box>
    </Box>
  );
}
