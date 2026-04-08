export type Indicator = 'environnement' | 'mobilite' | 'score'

export interface ArrondissementScores {
    environnement: number
    mobilite: number
    score: number
}

export type ScoresMap = Record<string, ArrondissementScores>
