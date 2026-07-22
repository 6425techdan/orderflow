// k6 profile: lunch rush (simulated elevated load)
// Honesty: still synthetic. Expect more queue age; may burn lab error budget.

import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE = __ENV.ORDERFLOW_API_URL || 'http://localhost:8080';

export const options = {
  scenarios: {
    lunch_rush: {
      executor: 'ramping-arrival-rate',
      startRate: 5,
      timeUnit: '1s',
      preAllocatedVUs: 20,
      maxVUs: 80,
      stages: [
        { duration: '30s', target: 15 },
        { duration: '2m', target: 25 },
        { duration: '30s', target: 5 },
      ],
    },
  },
  thresholds: {
    // Intentionally looser — lunch is a stress demo, not a production SLA claim.
    http_req_failed: ['rate<0.15'],
    http_req_duration: ['p(95)<1500'],
  },
  tags: { profile: 'lunch_rush', simulated: 'true' },
};

export default function () {
  const idem = `lunch-${__VU}-${__ITER}-${Date.now()}`;
  const res = http.post(
    `${BASE}/v1/orders`,
    JSON.stringify({
      location_id: 150 + (__VU % 80),
      idempotency_key: idem,
      items: [
        { sku: 'burger', quantity: 1, unit_price_cents: 799 },
        { sku: 'fries', quantity: 1, unit_price_cents: 299 },
      ],
      customer_ref: 'k6-lunch',
    }),
    {
      headers: {
        'Content-Type': 'application/json',
        'X-Correlation-ID': idem,
      },
    },
  );
  check(res, { 'accept 2xx': (r) => r.status >= 200 && r.status < 300 });
  sleep(0.05);
}
