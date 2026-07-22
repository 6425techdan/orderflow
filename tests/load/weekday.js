// k6 profile: weekday baseline (simulated)
// Honesty: synthetic RPS for a local lab — not real restaurant volume.

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter } from 'k6/metrics';

const BASE = __ENV.ORDERFLOW_API_URL || 'http://localhost:8080';
const accepted = new Counter('orderflow_k6_accepted');

export const options = {
  scenarios: {
    weekday: {
      executor: 'constant-arrival-rate',
      rate: 5,
      timeUnit: '1s',
      duration: '2m',
      preAllocatedVUs: 5,
      maxVUs: 20,
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.05'],
    http_req_duration: ['p(95)<500'],
  },
  tags: { profile: 'weekday', simulated: 'true' },
};

export default function () {
  const idem = `weekday-${__VU}-${__ITER}-${Date.now()}`;
  const payload = JSON.stringify({
    location_id: 100 + (__VU % 30),
    idempotency_key: idem,
    items: [{ sku: 'burger', quantity: 1, unit_price_cents: 799 }],
    customer_ref: 'k6-weekday',
  });
  const res = http.post(`${BASE}/v1/orders`, payload, {
    headers: {
      'Content-Type': 'application/json',
      'X-Correlation-ID': idem,
    },
  });
  const ok = check(res, {
    'accept 2xx': (r) => r.status >= 200 && r.status < 300,
  });
  if (ok) accepted.add(1);
  sleep(0.1);
}
