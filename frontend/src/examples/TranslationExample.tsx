// Exemples d'utilisation des traductions avec les nouvelles clés françaises

import { useLanguage } from '@/contexts/LanguageContext'

export default function ExampleUsage() {
  const { t } = useLanguage()

  return (
    <div className="p-4">
      <h1>{t('verification_imei')}</h1>
      <p>{t('invite_imei')}</p>
      
      <form>
        <label>{t('libelle_imei')}</label>
        <input type="text" placeholder={t('format_imei')} />
        <button type="submit">{t('verifier_imei')}</button>
      </form>
      
      <div className="results">
        <h2>{t('titre_resultats')}</h2>
        <p>{t('details_imei', { imei: '123456789012345' })}</p>
        
        <div className="summary">
          <h3>{t('resume')}</h3>
          <ul>
            <li>{t('base_locale')}: {t('trouve')}</li>
            <li>{t('tac_valide')}: {t('invalide_luhn')}</li>
            <li>{t('luhn_valide')}: {t('invalide_luhn')}</li>
          </ul>
        </div>
        
        <div className="local-search">
          <h3>{t('recherche_locale')}</h3>
          <p>{t('statut')}: {t('trouve')}</p>
          <p>{t('etat')}: actif</p>
          <p>{t('marque')}: Apple</p>
          <p>{t('modele')}: iPhone 14</p>
        </div>
        
        <div className="tac-validation">
          <h3>{t('validation_tac')}</h3>
          <p>{t('tac')}: 12345678</p>
          <p>{t('libelle_tac_valide')}: Non</p>
          <p>{t('libelle_luhn_valide')}: Non</p>
          <p>{t('source')}: luhn_only</p>
        </div>
        
        <div className="tac-details">
          <h3>{t('details_tac')}</h3>
          <p>{t('tac_non_trouve')}</p>
        </div>
        
        <div className="analysis-summary">
          <h3>{t('analyse_complete_effectuee')}</h3>
          <p>{t('description_analyse_complete')}</p>
          <p>{t('horodatage')}: {new Date().toLocaleString()}</p>
        </div>
      </div>
      
      <button type="button">{t('nouvelle_recherche')}</button>
    </div>
  )
}

// Instructions d'utilisation :
// 1. Importez useLanguage depuis le contexte
// 2. Utilisez la fonction t() avec les clés françaises
// 3. Pour les paramètres dynamiques, utilisez la syntaxe : t('details_imei', { imei: '123...' })
// 4. Toutes les clés sont maintenant en français pour une meilleure lisibilité
