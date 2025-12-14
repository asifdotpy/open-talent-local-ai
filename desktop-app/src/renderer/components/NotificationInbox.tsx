'use client';
import { Inbox } from '@novu/nextjs';

type Props = {
  subscriberId?: string;
};

export default function NotificationInbox({ subscriberId }: Props) {
  const applicationIdentifier = process.env.NEXT_PUBLIC_NOVU_APPLICATION_IDENTIFIER as string | undefined;
  const backendUrl = process.env.NEXT_PUBLIC_NOVU_BACKEND_URL as string | undefined;
  const socketUrl = process.env.NEXT_PUBLIC_NOVU_SOCKET_URL as string | undefined;

  const resolvedSubscriberId = subscriberId ?? '693e660cfaa9c95d04cbf3a1';

  return (
    <Inbox
      applicationIdentifier={applicationIdentifier as string}
      subscriberId={resolvedSubscriberId}
      {...(backendUrl ? { backendUrl } : {})}
      {...(socketUrl ? { socketUrl } : {})}
      appearance={{
        variables: {},
        elements: {},
        icons: {},
      }}
    />
  );
}
