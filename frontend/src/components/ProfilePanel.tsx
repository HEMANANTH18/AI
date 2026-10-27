import React, { useState } from "react";
import { CitizenProfile } from "../types";
import { getTranslation } from "../i18n/translations";
import { UserCheck, Edit3, Check } from "lucide-react";

interface ProfilePanelProps {
  profile: CitizenProfile;
  isComplete: boolean;
  selectedLanguage: string;
  onUpdateProfile: (updated: CitizenProfile) => void;
}

export const ProfilePanel: React.FC<ProfilePanelProps> = ({
  profile,
  isComplete,
  selectedLanguage,
  onUpdateProfile,
}) => {
  const t = getTranslation(selectedLanguage);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState<CitizenProfile>(profile);

  React.useEffect(() => {
    setFormData(profile);
  }, [profile]);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    onUpdateProfile(formData);
    setIsEditing(false);
  };

  return (
    <div className="bg-white rounded-3xl border border-slate-200 p-5 shadow-sm mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2.5">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${isComplete ? "bg-emerald-100 text-emerald-700" : "bg-blue-100 text-blue-700"}`}>
            <UserCheck className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-slate-900">{t.profileTitle}</h3>
            <p className="text-xs text-slate-500">{t.profileSubtitle}</p>
          </div>
        </div>

        <button
          onClick={() => setIsEditing(!isEditing)}
          className="flex items-center space-x-1 text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 transition-colors"
        >
          <Edit3 className="w-3.5 h-3.5 mr-1" />
          <span>{isEditing ? t.cancelEdit : t.editProfile}</span>
        </button>
      </div>

      {isEditing ? (
        <form onSubmit={handleSave} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 pt-2">
          {/* Age */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">{t.labelAge}</label>
            <input
              type="number"
              value={formData.age ?? ""}
              onChange={(e) => setFormData({ ...formData, age: e.target.value ? Number(e.target.value) : null })}
              placeholder="e.g. 35"
              className="w-full text-xs p-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          {/* Annual Income */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">{t.labelIncome}</label>
            <input
              type="number"
              value={formData.annual_income ?? ""}
              onChange={(e) => setFormData({ ...formData, annual_income: e.target.value ? Number(e.target.value) : null })}
              placeholder="e.g. 180000"
              className="w-full text-xs p-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          {/* State */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">{t.labelState}</label>
            <input
              type="text"
              value={formData.state ?? ""}
              onChange={(e) => setFormData({ ...formData, state: e.target.value || null })}
              placeholder="e.g. Tamil Nadu"
              className="w-full text-xs p-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          {/* Occupation */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">{t.labelOccupation}</label>
            <select
              value={formData.occupation ?? ""}
              onChange={(e) => setFormData({ ...formData, occupation: e.target.value || null })}
              className="w-full text-xs p-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-none bg-white"
            >
              <option value="">-- Select --</option>
              <option value="farmer">Farmer / Agriculture</option>
              <option value="student">Student / Scholar</option>
              <option value="construction_worker">Construction Worker</option>
              <option value="artisan">Artisan / Weaver</option>
              <option value="self_employed">Self Employed / MSME</option>
              <option value="unemployed">Unemployed</option>
              <option value="salaried">Salaried Employee</option>
            </select>
          </div>

          {/* Gender */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">{t.labelGender}</label>
            <select
              value={formData.gender ?? ""}
              onChange={(e) => setFormData({ ...formData, gender: e.target.value || null })}
              className="w-full text-xs p-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-none bg-white"
            >
              <option value="">-- Select --</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Transgender">Transgender</option>
            </select>
          </div>

          {/* Social Category */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">{t.labelCategory}</label>
            <select
              value={formData.social_category ?? ""}
              onChange={(e) => setFormData({ ...formData, social_category: e.target.value || null })}
              className="w-full text-xs p-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-none bg-white"
            >
              <option value="">-- Select --</option>
              <option value="General">General</option>
              <option value="OBC">OBC</option>
              <option value="SC">SC</option>
              <option value="ST">ST</option>
              <option value="Minority">Minority</option>
            </select>
          </div>

          {/* Disability */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">{t.labelDisability}</label>
            <select
              value={formData.disability === true ? "yes" : formData.disability === false ? "no" : ""}
              onChange={(e) => setFormData({ ...formData, disability: e.target.value === "yes" ? true : e.target.value === "no" ? false : null })}
              className="w-full text-xs p-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-none bg-white"
            >
              <option value="">-- Unknown --</option>
              <option value="no">No</option>
              <option value="yes">Yes (Divyangjan)</option>
            </select>
          </div>

          {/* Actions */}
          <div className="flex items-end space-x-2">
            <button
              type="submit"
              className="w-full flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg bg-blue-700 text-white text-xs font-semibold hover:bg-blue-800 transition-colors"
            >
              <Check className="w-3.5 h-3.5" />
              <span>{t.applyChanges}</span>
            </button>
          </div>
        </form>
      ) : (
        /* Summary view chips */
        <div className="flex flex-wrap items-center gap-2">
          <div className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs">
            <span className="text-slate-400 font-medium">{t.labelState}:</span>{" "}
            <strong className="text-slate-800">{profile.state || "Not specified"}</strong>
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs">
            <span className="text-slate-400 font-medium">{t.labelOccupation}:</span>{" "}
            <strong className="text-slate-800">{profile.occupation || "Not specified"}</strong>
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs">
            <span className="text-slate-400 font-medium">{t.labelAge}:</span>{" "}
            <strong className="text-slate-800">{profile.age ? `${profile.age} yrs` : "Not specified"}</strong>
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs">
            <span className="text-slate-400 font-medium">{t.labelIncome}:</span>{" "}
            <strong className="text-slate-800">
              {profile.annual_income != null ? `₹${profile.annual_income.toLocaleString("en-IN")}` : "Not specified"}
            </strong>
          </div>
          {profile.gender && (
            <div className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs">
              <span className="text-slate-400 font-medium">{t.labelGender}:</span>{" "}
              <strong className="text-slate-800">{profile.gender}</strong>
            </div>
          )}
          {profile.social_category && (
            <div className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs">
              <span className="text-slate-400 font-medium">{t.labelCategory}:</span>{" "}
              <strong className="text-slate-800">{profile.social_category}</strong>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
