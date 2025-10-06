import { VStack, Text, Box } from "@chakra-ui/react";

const menuItems = ["Dashboard", "Processos", "Drivers", "Configurações"];

export default function Sidebar() {
  return (
    <VStack
      bg="gray.900"
      w="64" // largura fixa
      minH="100vh"
      p={6}
      gap={4} // substitui spacing
      align="stretch"
      shadow="md"
    >
      <Text fontSize="2xl" fontWeight="bold" mb={6} color="blue.300">
        MachineMonitorZ
      </Text>

      {menuItems.map((item) => (
        <Box
          key={item}
          p={3}
          borderRadius="md"
          cursor="pointer"
          _hover={{ bg: "gray.700", color: "blue.300" }}
          fontWeight="medium"
        >
          {item}
        </Box>
      ))}
    </VStack>
  );
}
