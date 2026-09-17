import { emptyConstraints, type Profile, type ResumeDocument } from "../types/profile";

// 画像和简历解析历史共用同一个 localStorage key
export const STORAGE_KEY = "careerpilot:profile";
const MAX_RESUME_HISTORY = 3;

interface ProfileStore {
  profile: Profile | null;
  resumeHistory: Profile[]; // 最新的在前，最多 MAX_RESUME_HISTORY 条
}

function emptyStore(): ProfileStore {
  return { profile: null, resumeHistory: [] };
}

function loadStore(): ProfileStore {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return emptyStore();
    return JSON.parse(raw) as ProfileStore;
  } catch {
    return emptyStore();
  }
}

function writeStore(store: ProfileStore): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  } catch {
    // localStorage 不可用（隐私模式/容量超限）时静默失败，不影响页面使用
  }
}

export function getCurrentProfile(): Profile | null {
  return loadStore().profile;
}

export function getResumeHistory(): Profile[] {
  return loadStore().resumeHistory;
}

// 简历解析完成后调用：按 Profile schema 的格式存（画像专属字段没填过就留空，填过就保留），并把这份解析结果计入最近 3 份历史
export function saveParsedResume(resume: ResumeDocument): Profile {
  const store = loadStore();
  const constraints = store.profile?.constraints ?? emptyConstraints();
  const profile: Profile = { resume, constraints };

  store.profile = profile;
  store.resumeHistory = [profile, ...store.resumeHistory].slice(0, MAX_RESUME_HISTORY);
  writeStore(store);

  return profile;
}

// 画像成功保存到后端（PUT /profile）之后调用，把服务端返回的最终结果同步回本地缓存
export function saveProfile(profile: Profile): Profile {
  const store = loadStore();
  store.profile = profile;
  writeStore(store);
  return profile;
}
