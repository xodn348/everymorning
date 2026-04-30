'use server'

import { createClient } from '@supabase/supabase-js'

const MAX_KEYWORDS = 3

type ExistingSubscriber = {
  id: string
  telegram_chat_id?: string | null
}

function normalizeEmail(raw: FormDataEntryValue | null) {
  return typeof raw === 'string' ? raw.trim().toLowerCase() : ''
}

function parseKeywords(raw: FormDataEntryValue | null) {
  if (!raw || typeof raw !== 'string') {
    return []
  }

  return raw
    .split(',')
    .map((keyword) => keyword.trim().toLowerCase())
    .filter(Boolean)
    .slice(0, MAX_KEYWORDS)
}

function chooseTelegramChatId(subscribers: ExistingSubscriber[]) {
  return subscribers.find((subscriber) => subscriber.telegram_chat_id)?.telegram_chat_id ?? null
}

export async function subscribe(formData: FormData) {
  const email = normalizeEmail(formData.get('email'))
  const fields = formData.getAll('fields') as string[]
  const keywords = parseKeywords(formData.get('keywords'))
  
  if (!email || !email.includes('@')) {
    return { error: 'Please enter a valid email address' }
  }
  
  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_ANON_KEY!
  )
  
  const preferredFields = fields.length > 0 ? fields : null
  const preferredKeywords = keywords.length > 0 ? keywords : null

  const existing = await supabase
    .from('subscribers')
    .select('id,telegram_chat_id')
    .ilike('email', email)

  if (existing.error) {
    console.error('Duplicate subscription check error:', existing.error)
    return { error: 'Something went wrong' }
  }

  const replacingExisting = Boolean(existing.data && existing.data.length > 0)
  const telegramChatId = existing.data ? chooseTelegramChatId(existing.data) : null

  if (replacingExisting) {
    const deactivate = await supabase
      .from('subscribers')
      .update({ is_active: false, telegram_chat_id: null })
      .ilike('email', email)

    if (deactivate.error) {
      console.error('Existing subscription replacement error:', deactivate.error)
      return { error: 'Something went wrong' }
    }
  }

  const subscriber = {
    email,
    telegram_chat_id: telegramChatId,
    preferred_fields: preferredFields,
    preferred_keywords: preferredKeywords,
  }

  let { error } = await supabase
    .from('subscribers')
    .insert(subscriber)

  // Keep existing subscriptions working until the production DB migration is applied.
  if (error && error.message?.includes('preferred_keywords')) {
    const fallback = await supabase
      .from('subscribers')
      .insert({
        email,
        preferred_fields: preferredFields,
      })
    error = fallback.error
  }
  
  if (error) {
    if (error.code === '23505') {
      return { error: 'Already subscribed!' }
    }
    console.error('Subscription error:', error)
    return { error: 'Something went wrong' }
  }
  
  return { success: true, replaced: replacingExisting }
}

export async function unsubscribe(email: string) {
  email = email.trim().toLowerCase()

  if (!email || !email.includes('@')) {
    return { error: 'Invalid email address' }
  }
  
  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_ANON_KEY!
  )
  
  const { error } = await supabase
    .from('subscribers')
    .update({ is_active: false })
    .eq('email', email)
  
  if (error) {
    console.error('Unsubscribe error:', error)
    return { error: 'Something went wrong' }
  }
  
  return { success: true }
}
