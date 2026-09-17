const fetch = require('node-fetch');

const gateway_url = (typeof $vars !== 'undefined' && $vars.gateway_url) ? $vars.gateway_url : 'http://192.168.50.10:8000';
const group_id = (typeof $vars !== 'undefined' && $vars.group_id) ? $vars.group_id : 'GROUP01';

const targetSensor = typeof $sensor !== 'undefined' ? $sensor : '';

const allowed = ['light', 'temperature', 'acceleration', 'buttons'];
if (!allowed.includes(targetSensor)) {
  return JSON.stringify({ status: 'error', error: `unsupported sensor: "${targetSensor}". Please check Flowise tool parameters name sensor` });
}

const body = { action: `read_${targetSensor}` };

try {
  const response = await fetch(
    `${gateway_url}/v1/devices/${group_id}/command`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    }
  );

  const text = await response.text();
  if (!response.ok) {
    return JSON.stringify({ status: 'error', http_status: response.status, detail: text });
  }
  return text;
} catch (err) {
  return JSON.stringify({ status: 'error', error: err.message });
}
