// PasswordStrengthInput.tsx
import React, { useState } from "react";
import {
  PasswordInput,
  Popover,
  Box,
  Progress,
  Text,
  Stack,
} from "@mantine/core";
import { IconCheck, IconX } from "@tabler/icons-react";

function PasswordRequirement({
  meets,
  label,
}: {
  meets: boolean;
  label: string;
}) {
  return (
    <Text
      c={meets ? "teal" : "red"}
      sx={{ display: "flex", alignItems: "center" }}
      mt={7}
      size="sm"
    >
      {meets ? <IconCheck size="0.9rem" /> : <IconX size="0.9rem" />}{" "}
      <Box ml={10}>{label}</Box>
    </Text>
  );
}

const requirements = [
  { re: /[0-9]/, label: "Includes number" },
  { re: /[a-z]/, label: "Includes lowercase letter" },
  { re: /[A-Z]/, label: "Includes uppercase letter" },
  { re: /[!@#$%^&*]/, label: "Includes special symbol from !@#$%^&*" },
  // TODO: Add this, but logic must be flipped
  // {
  //   re: /(.)\1{3,}/,
  //   label: "No repeated characters in sequence four times or more",
  // },
];

function getStrength(password: string) {
  let multiplier = password.length > 5 ? 0 : 1;

  requirements.forEach((requirement) => {
    if (!requirement.re.test(password)) {
      multiplier += 1;
    }
  });

  return Math.max(100 - (100 / (requirements.length + 1)) * multiplier, 10);
}

interface PasswordStrengthInputProps {
  form: any;
  isLoading: boolean;
  visible: boolean;
  toggle: () => void;
}

const PasswordStrengthInput: React.FC<PasswordStrengthInputProps> = ({
  form,
  isLoading,
  visible,
  toggle,
}) => {
  const [popoverOpened, setPopoverOpened] = useState(false);

  const checks = requirements.map((requirement, index) => (
    <PasswordRequirement
      key={index}
      label={requirement.label}
      meets={requirement.re.test(form.values.password1)}
    />
  ));

  const strength = getStrength(form.values.password1);
  const color = strength === 100 ? "teal" : strength > 50 ? "yellow" : "red";

  return (
    <Stack gap={0}>
      <Box>
        <Popover
          opened={popoverOpened}
          position="bottom"
          width="target"
          transitionProps={{ transition: "pop" }}
        >
          <Popover.Target>
            <div
              onFocusCapture={() => setPopoverOpened(true)}
              onBlurCapture={() => setPopoverOpened(false)}
            >
              <PasswordInput
                id="p1"
                label="Password"
                placeholder="Your password"
                required
                style={{ marginTop: 15 }}
                {...form.getInputProps("password1")}
                disabled={isLoading}
                visible={visible}
                onVisibilityChange={toggle}
              />
            </div>
          </Popover.Target>
          <Popover.Dropdown>
            <Progress color={color} value={strength} size={5} mb="xs" />
            <PasswordRequirement
              label="Includes at least 8 characters"
              meets={form.values.password1.length > 7}
            />
            {checks}
          </Popover.Dropdown>
        </Popover>
      </Box>
      <PasswordInput
        id="p2"
        label="Repeat Password"
        placeholder="Repeat your password"
        required
        style={{ marginTop: 15 }}
        {...form.getInputProps("password2")}
        disabled={isLoading}
        visible={visible}
        onVisibilityChange={toggle}
      />
    </Stack>
  );
};

export default PasswordStrengthInput;
