const fetch = require('node-fetch');
const allowedActions = ['show_icon', 'clear_display', 'play_tone'];
const allowedIcons = ['HAPPY','SAD','YES','NO','HEART','SURPRISED','ASLEEP'];
if (!allowedActions.includes($action)) return JSON.stringify({status:'error', error:'unsupported action'});
 
const body = {action: $action};
if ($action === 'show_icon') {
  if (!allowedIcons.includes($icon)) return JSON.stringify({status:'error', error:'unsupported icon'});
  body.icon = $icon;
}
if ($action === 'play_tone') {
  body.frequency = Number($frequency);
  body.duration_ms = Number($duration_ms);
}
 
const response = await fetch(
  `${$vars.gateway_url}/v1/devices/${$vars.group_id}/command`,
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  }
);
const text = await response.text();
if (!response.ok) return JSON.stringify({status:'error', http_status:response.status, detail:text});
return text;
