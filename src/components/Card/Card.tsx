import { Box, Text, Flex } from "@chakra-ui/react";

interface Props {
  title: string;
  value: string;
  color?: string;
}

export default function MetricCard({ title, value, color = "blue.400" }: Props) {
  return (
    <Box
      bg="gray.800"
      borderRadius="md"
      shadow="md"
      p={4}
      borderLeft={`4px solid ${color}`}
      _hover={{ shadow: "lg", transform: "translateY(-2px)", transition: "0.2s" }}
    >
      <Flex direction="column">
        <Text fontSize="md" fontWeight="bold" color="gray.300">
          {title}
        </Text>
        <Text fontSize="3xl" fontWeight="extrabold" mt={2} color={color}>
          {value}
        </Text>
      </Flex>
    </Box>
  );
}
