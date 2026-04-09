export type Indicator = 'environnement' | 'mobilite' | 'score' | 'aucun'

export interface ArrondissementScores {
    environnement: number
    mobilite: number
    score: number
}

export type ScoresMap = Record<string, ArrondissementScores>
