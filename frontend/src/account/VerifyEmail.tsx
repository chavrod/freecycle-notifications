import { useState } from "react";

import { Button, Text, Stack, Title } from "@mantine/core";
import { useLoaderData, Navigate, LoaderFunctionArgs } from "react-router-dom";

import { AuthRes } from "../auth/AuthContext";
import { getEmailVerification, verifyEmail } from "../auth/api";
import notifyError from "../utils/notifyError";

export async function loader({ params }: LoaderFunctionArgs) {
  const key = params.key;
  const resp = await getEmailVerification(key);
  return { key, verification: resp };
}

export default function VerifyEmail() {
  const { key, verification } = useLoaderData();

  const [confirmationRes, setConfirmationRes] = useState<{
    fetching: boolean;
    content: AuthRes | null;
  }>({ fetching: false, content: null });

  function submit() {
    setConfirmationRes({ ...confirmationRes, fetching: true });
    verifyEmail(key)
      .then((content) => {
        setConfirmationRes((r) => {
          return { ...r, content };
        });
        if (content.status == 500) {
          notifyError({ message: content.data });
        }
      })
      .catch((e) => {
        notifyError({ message: e.data });
      })
      .then(() => {
        setConfirmationRes((r) => {
          return { ...r, fetching: false };
        });
      });
  }

  if (
    confirmationRes.content &&
    [200, 401].includes(confirmationRes.content?.status)
  ) {
    return <Navigate to="/account/login?email=verified" />;
  }
  if (!verification) {
    return <></>;
  }

  let body = null;
  if (verification.status === 200) {
    body = (
      <>
        <Text>
          Please confirm that{" "}
          <a href={"mailto:" + verification.data.email}>
            {verification.data.email}
          </a>{" "}
          is an email address for user {verification?.data?.user?.username}.
        </Text>
        <Button
          size="lg"
          disabled={confirmationRes.fetching}
          loading={confirmationRes.fetching}
          onClick={() => submit()}
        >
          Confirm
        </Button>
      </>
    );
  } else if (!verification.data?.email) {
    body = <Text>Invalid verification link.</Text>;
  } else {
    body = (
      <Text>
        Unable to confirm email{" "}
        <a href={"mailto:" + verification.data.email}>
          {verification.data.email}
        </a>{" "}
        because it is already confirmed.
      </Text>
    );
  }
  return (
    <Stack m="xl" h="calc(100vh - 210px)" align="center" justify="center">
      <Title order={2}>Confirm Email Address</Title>
      {body}
    </Stack>
  );
}
