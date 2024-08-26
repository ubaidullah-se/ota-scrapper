const proxies = [
  "5.59.251.30:6069",
  "5.59.250.229:6927",
  "5.59.250.29:6727",
  "5.59.251.211:6250",
  "5.59.251.17:6056",
  "5.59.250.85:6783",
  "5.59.250.250:6948",
  "5.59.250.95:6793",
  "5.59.251.90:6129",
  "5.59.250.172:6870",
  "5.59.251.61:6100",
  "5.59.250.60:6758",
  "5.59.250.139:6837",
  "5.59.251.191:6230",
  "5.59.251.223:6262",
  "5.59.251.107:6146",
  "5.59.250.125:6823",
  "5.59.250.254:6952",
  "5.59.250.160:6858",
  "5.59.250.185:6883",
];

// Set the proxy settings for Chrome
function setProxy(proxyIP, proxyPort, proxyUsername, proxyPassword) {
  // Create a proxy rule
  const proxyConfig = {
    mode: "fixed_servers",
    rules: {
      singleProxy: {
        scheme: "http",
        host: proxyIP,
        port: parseInt(proxyPort),
      },
      bypassList: [],
    },
  };

  // Update the proxy settings
  chrome.proxy.settings.set(
    { value: proxyConfig, scope: "regular" },
    function () {
      if (chrome.runtime.lastError) {
        console.error("Error setting proxy:", chrome.runtime.lastError);
      }
    }
  );

  chrome.webRequest.onAuthRequired.addListener(
    function (details) {
      return {
        authCredentials: {
          username: proxyUsername,
          password: proxyPassword,
        },
      };
    },
    { urls: ["<all_urls>"] },
    ["blocking"]
  );
}

let currentProxyIndex = 0;

function rotateProxy() {
  let proxy = proxies[currentProxyIndex];
  currentProxyIndex = (currentProxyIndex + 1) % proxies.length;
  let [proxyIP, proxyPort] = proxy.split(":");

  setProxy(proxyIP, proxyPort, "ccpxjgjt", "gxc7om4wg0tl");
}

chrome.tabs.onUpdated.addListener(function (tabId, changeInfo, tab) {
  rotateProxy();
});

chrome.tabs.onCreated.addListener(function () {
  rotateProxy();
});
