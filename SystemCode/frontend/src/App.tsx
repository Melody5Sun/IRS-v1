import { useState } from "react";
import { ResumeUpload } from "./components/ResumeUpload";
import { ProfileForm } from "./components/ProfileForm";
import { getCurrentProfile } from "./lib/profileStorage";
import type { Profile } from "./types/profile";

export function App() {
  const [profile, setProfile] = useState<Profile | null>(() => getCurrentProfile());

  return (
    <main>
      <h1>IT CareerPilot</h1>
      <ResumeUpload onParsed={setProfile} />
      {profile && <ProfileForm profile={profile} onSaved={setProfile} />}
      <pre>{JSON.stringify(profile, null, 2)}</pre>
    </main>
  );
}
