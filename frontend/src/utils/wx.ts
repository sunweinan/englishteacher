/* eslint-disable @typescript-eslint/no-explicit-any */
import axios from '@/utils/http';
import { API_ENDPOINTS } from '@/config/api';

interface WechatConfigResponse {
  appId: string;
  timestamp: string;
  nonceStr: string;
  signature: string;
}

interface PrepayParams {
  package: string;
  nonceStr: string;
  timeStamp: string;
  signType: string;
  paySign: string;
}

function loadJSSDK(): Promise<void> {
  return new Promise((resolve, reject) => {
    if ((window as any).wx) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://res.wx.qq.com/open/js/jweixin-1.6.0.js';
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load WeChat JS SDK'));
    document.head.appendChild(script);
  });
}

export async function initWechatSDK(url: string) {
  await loadJSSDK();
  const { data } = await axios.get<WechatConfigResponse>(API_ENDPOINTS.wechatConfig, { params: { url } });
  const wx = (window as any).wx;
  wx.config({
    debug: false,
    appId: data.appId,
    timestamp: data.timestamp,
    nonceStr: data.nonceStr,
    signature: data.signature,
    jsApiList: ['chooseWXPay']
  });
}

export async function callWechatPay(prepay: PrepayParams) {
  await loadJSSDK();
  const wx = (window as any).wx;
  return new Promise((resolve, reject) => {
    wx.chooseWXPay({
      ...prepay,
      success: resolve,
      fail: reject,
      cancel: reject
    });
  });
}

export async function createWechatOrder(payload: Record<string, any>) {
  const { data } = await axios.post(API_ENDPOINTS.wechatOrder, payload);
  return data;
}
