import type { UserRole } from '../../types/User';

export function NotificationLink(fireId: string, role: UserRole | null): string {
  let path: string;

  if (role === 'admin') {
    path = `/admin/live-map?fire=${fireId}`;
  } else if (role === 'firefighter') {
    path = `/firefighter/dashboard?fire=${fireId}`;
  } else if (role == 'user') {
    path = `/users/live-map?fire=${fireId}`;
  } else {
    path = `/guests/live-map?fire=${fireId}`;
  }

  return path;
}
