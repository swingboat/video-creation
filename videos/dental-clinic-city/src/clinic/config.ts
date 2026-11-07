import {useEffect, useState, type CSSProperties} from 'react';
import {cancelRender, continueRender, delayRender, staticFile} from 'remotion';

export type BuildingConfig = {id: string; position: [number, number]; width: number; height: number; depth: number; color: string};
export type MerchantConfig = {
  name: string; city: string; district: string; address: string; services: string[];
  highlights: {title: string; detail: string}[]; cta: string; locationNote: string;
  theme: {brand: string; background: string; marker: string};
  store: {position: [number, number]; width: number; height: number; depth: number};
  buildings: BuildingConfig[];
};
export type ClinicProps = {configSrc: string; style?: CSSProperties};

export const validateMerchant = (value: unknown): MerchantConfig => {
  if (!value || typeof value !== 'object') throw new Error('商家配置必须是 JSON 对象');
  const data = value as MerchantConfig;
  for (const key of ['name', 'city', 'district', 'address', 'cta', 'locationNote'] as const) {
    if (typeof data[key] !== 'string' || !data[key].trim()) throw new Error(`商家配置缺少 ${key}`);
  }
  if (!Array.isArray(data.services) || !data.services.length || data.services.some((s) => typeof s !== 'string')) {
    throw new Error('services 必须是非空字符串数组');
  }
  if (!Array.isArray(data.highlights) || data.highlights.length !== 3 || data.highlights.some((item) =>
    !item || typeof item.title !== 'string' || typeof item.detail !== 'string')) throw new Error('highlights 必须包含 3 个卖点');
  const colors = [data.theme?.brand, data.theme?.background, data.theme?.marker];
  if (colors.some((color) => typeof color !== 'string' || !/^#[\da-f]{6}$/i.test(color))) throw new Error('theme 颜色须为六位 HEX');
  const geometry = (item: MerchantConfig['store']) => item && Array.isArray(item.position) && item.position.length === 2 &&
    item.position.every(Number.isFinite) && [item.width, item.depth, item.height].every((n) => Number.isFinite(n) && n > 0);
  if (!geometry(data.store)) throw new Error('store 位置和尺寸无效');
  if (!Array.isArray(data.buildings) || data.buildings.some((b) => !geometry(b) || typeof b.id !== 'string' || !/^#[\da-f]{6}$/i.test(b.color))) {
    throw new Error('buildings 中有无效建筑');
  }
  return data;
};

const pending = new Map<string, Promise<MerchantConfig>>();
export const useMerchant = (configSrc: string) => {
  const [data, setData] = useState<MerchantConfig | null>(null);
  const [handle] = useState(() => delayRender('加载本地商家 JSON'));
  useEffect(() => {
    let active = true;
    let request = pending.get(configSrc);
    if (!request) {
      request = fetch(staticFile(configSrc)).then(async (response) => {
        if (!response.ok) throw new Error(`无法读取商家配置：${configSrc} (${response.status})`);
        return validateMerchant(await response.json());
      });
      pending.set(configSrc, request);
    }
    request.then((merchant) => {if (active) setData(merchant);}).catch((error: unknown) => {if (active) cancelRender(error);});
    return () => {active = false; continueRender(handle);};
  }, [configSrc, handle]);
  useEffect(() => {if (data) continueRender(handle);}, [data, handle]);
  return data;
};

export const configSchema = {
  configSrc: {type: 'text-content' as const, default: 'business/clinic.json', description: 'public 目录内的商家 JSON 路径'},
};
