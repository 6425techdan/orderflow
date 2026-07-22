// k6 profile: stadium surge (simulated stress / budget-burn demo)
// Honesty: NOT real venue traffic. Expect degradation. Measure it; do not hide it.

import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE = __ENV.ORDERFLOW_API_URL || 'http://localhost:8080';

export const options = {
  scenarios: {
    stadium_surge: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 200,
      stages: [
        { duration: '20s', target: 40 },
        { duration: '1m', target: 80 },
        { duration: '1m', target: 120 },
        { duration: '30s', target: 10 },
      ],
    },
  },
  thresholds: {
    // Soft thresholds: surge is meant to show pain and recovery, not "pass green at all costs".
    http_req_failed: ['rate<0.4'],
    http_req_duration: ['p(95)<5000'],
  },
  tags: { profile: 'stadium_surge', simulated: 'true' },
};

export default function () {
  const idem = `stadium-${__VU}-${__ITER}-${Date.now()}`;
  const res = http.post(
    `${BASE}/v1/orders`,
    JSON.stringify({
      location_id: 200 + (__VU % 120),
      idempotency_key: idem,
      items: [{ sku: 'combo', quantity: 2, unit_price_cents: 1299 }],
      customer_ref: 'k6-stadium',
    }),
    {
      headers: {
        'Content-Type': 'application/json',
        'X-Correlation-ID': idem,
      },
    },
  );
  check(res, {
    'status not 5xx preferred': (r) => r.status < 500,
  });
  sleep(0.02);
}
